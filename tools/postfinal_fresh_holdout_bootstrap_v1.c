/*
 * Dependency-free, strictly framed paired bootstrap for the unopened fresh
 * holdout.  This program never opens a case, file, candidate, clock, or key.
 * The independently guarded controller supplies only completed paired
 * observations and the already domain-separated, nonsecret bootstrap seed.
 *
 * Request, little endian: <8sHHIII32sQ
 *   RBHBOOT1, version 1, operation 1 or 2, 19, 2000, candidate 0..2,
 *   32 nonzero seed bytes, case 0..65535 or UINT64_MAX for aggregates.
 * Operation 1 then supplies 19 interleaved positive baseline/candidate u64
 * pairs.  Operation 2 supplies 19 finite IEEE-754 binary64 mean-log ratios.
 *
 * Response, little endian: <8sHHIII32sQddd
 *   RBHRES01, the exact validated request metadata, and positive finite
 *   point estimate, lower order statistic 49, upper order statistic 1950.
 * Each confidence interval uses exactly 2000 xoshiro256** resamples of 19
 * paired trial values, with unbiased rejection sampling over the 19 trials.
 */

#include <float.h>
#include <limits.h>
#include <math.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

enum {
    REQUEST_HEADER_BYTES = 64,
    RESPONSE_FRAME_BYTES = 88,
    SEED_BYTES = 32,
    TRIALS = 19,
    BOOTSTRAP_DRAWS = 2000,
    CANDIDATES = 3,
    CASES = 65536,
    OP_CASE = 1,
    OP_AGGREGATE = 2,
    PROTOCOL_VERSION = 1,
    CASE_PAYLOAD_BYTES = TRIALS * 2 * 8,
    AGGREGATE_PAYLOAD_BYTES = TRIALS * 8,
    LOWER_ORDER_STATISTIC = 49,
    UPPER_ORDER_STATISTIC = 1950
};

_Static_assert(CHAR_BIT == 8, "the bootstrap wire requires eight-bit bytes");
_Static_assert(sizeof(uint64_t) == 8, "the bootstrap wire requires uint64_t");
_Static_assert(sizeof(double) == 8, "the bootstrap wire requires binary64");
_Static_assert(FLT_RADIX == 2, "the bootstrap wire requires binary floating point");
_Static_assert(DBL_MANT_DIG == 53, "the bootstrap wire requires binary64 precision");
_Static_assert(DBL_MAX_EXP == 1024, "the bootstrap wire requires binary64 range");
_Static_assert(REQUEST_HEADER_BYTES == 64, "the request header must be 64 bytes");
_Static_assert(RESPONSE_FRAME_BYTES == 88, "the response must be 88 bytes");
_Static_assert(CASE_PAYLOAD_BYTES == 304, "a case has 38 paired uint64 values");
_Static_assert(AGGREGATE_PAYLOAD_BYTES == 152, "an aggregate has 19 doubles");
_Static_assert(
    LOWER_ORDER_STATISTIC < UPPER_ORDER_STATISTIC
        && UPPER_ORDER_STATISTIC < BOOTSTRAP_DRAWS,
    "confidence order statistics must be within the frozen draw count"
);

static const uint8_t REQUEST_MAGIC[8] = {
    'R', 'B', 'H', 'B', 'O', 'O', 'T', '1'
};
static const uint8_t RESPONSE_MAGIC[8] = {
    'R', 'B', 'H', 'R', 'E', 'S', '0', '1'
};

typedef enum {
    FAILURE_NONE = 0,
    FAILURE_USAGE = 2,
    FAILURE_TRUNCATED_HEADER = 3,
    FAILURE_REQUEST_MAGIC = 4,
    FAILURE_VERSION = 5,
    FAILURE_OPERATION = 6,
    FAILURE_DENOMINATOR = 7,
    FAILURE_CANDIDATE = 8,
    FAILURE_SEED = 9,
    FAILURE_CASE_INDEX = 10,
    FAILURE_TRUNCATED_PAYLOAD = 11,
    FAILURE_NONPOSITIVE_TIMING = 12,
    FAILURE_NONFINITE_INPUT = 13,
    FAILURE_NONFINITE_STATISTIC = 14,
    FAILURE_OUTPUT = 15,
    FAILURE_SELF_TEST = 16,
    FAILURE_INPUT = 17
} Failure;

typedef struct {
    uint16_t version;
    uint16_t operation;
    uint32_t trials;
    uint32_t draws;
    uint32_t candidate;
    uint8_t seed[SEED_BYTES];
    uint64_t case_index;
    double log_ratios[TRIALS];
} Request;

typedef struct {
    uint64_t state[4];
} Xoshiro256;

typedef struct {
    double point;
    double lower;
    double upper;
} Interval;

static uint16_t load_le16(const uint8_t *bytes) {
    return (uint16_t)(
        (uint16_t)bytes[0]
        | ((uint16_t)bytes[1] << 8)
    );
}

static uint32_t load_le32(const uint8_t *bytes) {
    uint32_t value = 0;
    for (size_t index = 0; index < 4; index++) {
        value |= (uint32_t)bytes[index] << (unsigned)(index * 8);
    }
    return value;
}

static uint64_t load_le64(const uint8_t *bytes) {
    uint64_t value = 0;
    for (size_t index = 0; index < 8; index++) {
        value |= (uint64_t)bytes[index] << (unsigned)(index * 8);
    }
    return value;
}

static void store_le16(uint8_t *bytes, uint16_t value) {
    for (size_t index = 0; index < 2; index++) {
        bytes[index] = (uint8_t)(value >> (unsigned)(index * 8));
    }
}

static void store_le32(uint8_t *bytes, uint32_t value) {
    for (size_t index = 0; index < 4; index++) {
        bytes[index] = (uint8_t)(value >> (unsigned)(index * 8));
    }
}

static void store_le64(uint8_t *bytes, uint64_t value) {
    for (size_t index = 0; index < 8; index++) {
        bytes[index] = (uint8_t)(value >> (unsigned)(index * 8));
    }
}

static double load_le_double(const uint8_t *bytes) {
    const uint64_t bits = load_le64(bytes);
    double value;
    memcpy(&value, &bits, sizeof(value));
    return value;
}

static void store_le_double(uint8_t *bytes, double value) {
    uint64_t bits;
    memcpy(&bits, &value, sizeof(bits));
    store_le64(bytes, bits);
}

static Failure parse_header(
    const uint8_t header[REQUEST_HEADER_BYTES],
    Request *request
) {
    if (memcmp(header, REQUEST_MAGIC, sizeof(REQUEST_MAGIC)) != 0) {
        return FAILURE_REQUEST_MAGIC;
    }

    request->version = load_le16(header + 8);
    request->operation = load_le16(header + 10);
    request->trials = load_le32(header + 12);
    request->draws = load_le32(header + 16);
    request->candidate = load_le32(header + 20);
    memcpy(request->seed, header + 24, SEED_BYTES);
    request->case_index = load_le64(header + 56);

    if (request->version != PROTOCOL_VERSION) return FAILURE_VERSION;
    if (
        request->operation != OP_CASE
        && request->operation != OP_AGGREGATE
    ) {
        return FAILURE_OPERATION;
    }
    if (
        request->trials != TRIALS
        || request->draws != BOOTSTRAP_DRAWS
    ) {
        return FAILURE_DENOMINATOR;
    }
    if (request->candidate >= CANDIDATES) return FAILURE_CANDIDATE;

    uint8_t seed_bits = 0;
    for (size_t index = 0; index < SEED_BYTES; index++) {
        seed_bits |= request->seed[index];
    }
    if (seed_bits == 0) return FAILURE_SEED;

    if (
        (request->operation == OP_CASE && request->case_index >= CASES)
        || (
            request->operation == OP_AGGREGATE
            && request->case_index != UINT64_MAX
        )
    ) {
        return FAILURE_CASE_INDEX;
    }
    return FAILURE_NONE;
}

static size_t payload_length(const Request *request) {
    return request->operation == OP_CASE
        ? (size_t)CASE_PAYLOAD_BYTES
        : (size_t)AGGREGATE_PAYLOAD_BYTES;
}

static Failure parse_payload(
    Request *request,
    const uint8_t *payload,
    size_t length
) {
    if (length != payload_length(request)) return FAILURE_TRUNCATED_PAYLOAD;

    if (request->operation == OP_CASE) {
        for (size_t index = 0; index < TRIALS; index++) {
            const uint64_t baseline = load_le64(payload + index * 16);
            const uint64_t candidate = load_le64(payload + index * 16 + 8);
            if (baseline == 0 || candidate == 0) {
                return FAILURE_NONPOSITIVE_TIMING;
            }
            const double ratio = log((double)baseline) - log((double)candidate);
            if (!isfinite(ratio)) return FAILURE_NONFINITE_INPUT;
            request->log_ratios[index] = ratio;
        }
    } else {
        for (size_t index = 0; index < TRIALS; index++) {
            const double value = load_le_double(payload + index * 8);
            if (!isfinite(value)) return FAILURE_NONFINITE_INPUT;
            request->log_ratios[index] = value;
        }
    }
    return FAILURE_NONE;
}

static uint64_t rotate_left(const uint64_t value, const unsigned count) {
    return (value << count) | (value >> (64U - count));
}

static void initialize_rng(Xoshiro256 *random, const uint8_t seed[SEED_BYTES]) {
    for (size_t index = 0; index < 4; index++) {
        random->state[index] = load_le64(seed + index * 8);
    }
}

static uint64_t next_random(Xoshiro256 *random) {
    const uint64_t result = rotate_left(
        random->state[1] * UINT64_C(5),
        7U
    ) * UINT64_C(9);
    const uint64_t shifted = random->state[1] << 17U;

    random->state[2] ^= random->state[0];
    random->state[3] ^= random->state[1];
    random->state[1] ^= random->state[2];
    random->state[0] ^= random->state[3];
    random->state[2] ^= shifted;
    random->state[3] = rotate_left(random->state[3], 45U);
    return result;
}

static size_t uniform_trial(Xoshiro256 *random) {
    const uint64_t threshold =
        (UINT64_C(0) - UINT64_C(19)) % UINT64_C(19);
    uint64_t value;
    do {
        value = next_random(random);
    } while (value < threshold);
    return (size_t)(value % UINT64_C(19));
}

static int compare_finite_doubles(const void *left, const void *right) {
    const double a = *(const double *)left;
    const double b = *(const double *)right;
    return (a > b) - (a < b);
}

static Failure positive_exp(double log_value, double *result) {
    if (!isfinite(log_value)) return FAILURE_NONFINITE_STATISTIC;
    const double value = exp(log_value);
    if (!isfinite(value) || value <= 0.0) {
        return FAILURE_NONFINITE_STATISTIC;
    }
    *result = value;
    return FAILURE_NONE;
}

static Failure calculate_interval(const Request *request, Interval *interval) {
    double total = 0.0;
    for (size_t index = 0; index < TRIALS; index++) {
        total += request->log_ratios[index];
        if (!isfinite(total)) return FAILURE_NONFINITE_STATISTIC;
    }
    Failure failure = positive_exp(total / (double)TRIALS, &interval->point);
    if (failure != FAILURE_NONE) return failure;

    Xoshiro256 random;
    initialize_rng(&random, request->seed);
    double samples[BOOTSTRAP_DRAWS];
    for (size_t draw = 0; draw < BOOTSTRAP_DRAWS; draw++) {
        double sample = 0.0;
        for (size_t trial = 0; trial < TRIALS; trial++) {
            sample += request->log_ratios[uniform_trial(&random)];
            if (!isfinite(sample)) return FAILURE_NONFINITE_STATISTIC;
        }
        samples[draw] = sample / (double)TRIALS;
        if (!isfinite(samples[draw])) return FAILURE_NONFINITE_STATISTIC;
    }

    qsort(
        samples,
        (size_t)BOOTSTRAP_DRAWS,
        sizeof(samples[0]),
        compare_finite_doubles
    );
    failure = positive_exp(samples[LOWER_ORDER_STATISTIC], &interval->lower);
    if (failure != FAILURE_NONE) return failure;
    failure = positive_exp(samples[UPPER_ORDER_STATISTIC], &interval->upper);
    if (failure != FAILURE_NONE) return failure;
    if (interval->lower > interval->upper) {
        return FAILURE_NONFINITE_STATISTIC;
    }
    return FAILURE_NONE;
}

static void encode_response(
    const Request *request,
    const Interval *interval,
    uint8_t response[RESPONSE_FRAME_BYTES]
) {
    memcpy(response, RESPONSE_MAGIC, sizeof(RESPONSE_MAGIC));
    store_le16(response + 8, request->version);
    store_le16(response + 10, request->operation);
    store_le32(response + 12, request->trials);
    store_le32(response + 16, request->draws);
    store_le32(response + 20, request->candidate);
    memcpy(response + 24, request->seed, SEED_BYTES);
    store_le64(response + 56, request->case_index);
    store_le_double(response + 64, interval->point);
    store_le_double(response + 72, interval->lower);
    store_le_double(response + 80, interval->upper);
}

static Failure process_frame(
    const uint8_t header[REQUEST_HEADER_BYTES],
    const uint8_t *payload,
    size_t payload_bytes,
    uint8_t response[RESPONSE_FRAME_BYTES]
) {
    Request request;
    memset(&request, 0, sizeof(request));
    Failure failure = parse_header(header, &request);
    if (failure != FAILURE_NONE) return failure;
    failure = parse_payload(&request, payload, payload_bytes);
    if (failure != FAILURE_NONE) return failure;
    Interval interval;
    failure = calculate_interval(&request, &interval);
    if (failure != FAILURE_NONE) return failure;
    encode_response(&request, &interval, response);
    return FAILURE_NONE;
}

static Failure read_remaining(uint8_t *bytes, size_t count) {
    size_t received = 0;
    while (received < count) {
        const size_t portion = fread(bytes + received, 1, count - received, stdin);
        if (portion == 0) {
            return ferror(stdin) ? FAILURE_INPUT : FAILURE_TRUNCATED_PAYLOAD;
        }
        received += portion;
    }
    return FAILURE_NONE;
}

static int fail_closed(Failure failure) {
    static const char *const messages[] = {
        [FAILURE_USAGE] = "invalid bootstrap command",
        [FAILURE_TRUNCATED_HEADER] = "truncated bootstrap request header",
        [FAILURE_REQUEST_MAGIC] = "invalid bootstrap request magic",
        [FAILURE_VERSION] = "invalid bootstrap protocol version",
        [FAILURE_OPERATION] = "invalid bootstrap operation",
        [FAILURE_DENOMINATOR] = "invalid frozen paired-bootstrap denominator",
        [FAILURE_CANDIDATE] = "invalid bootstrap candidate index",
        [FAILURE_SEED] = "invalid all-zero bootstrap seed",
        [FAILURE_CASE_INDEX] = "invalid bootstrap case index",
        [FAILURE_TRUNCATED_PAYLOAD] = "truncated bootstrap request payload",
        [FAILURE_NONPOSITIVE_TIMING] = "nonpositive paired timing",
        [FAILURE_NONFINITE_INPUT] = "nonfinite paired bootstrap input",
        [FAILURE_NONFINITE_STATISTIC] = "nonfinite paired bootstrap statistic",
        [FAILURE_OUTPUT] = "failed to write bootstrap response",
        [FAILURE_SELF_TEST] = "bootstrap synthetic self-test failed",
        [FAILURE_INPUT] = "failed to read bootstrap request"
    };
    const size_t index = (size_t)failure;
    const char *message =
        index < sizeof(messages) / sizeof(messages[0])
            && messages[index] != NULL
        ? messages[index]
        : "invalid bootstrap failure state";
    (void)fprintf(stderr, "rebar-bootstrap-v1: %s\n", message);
    return (int)failure;
}

static int stream_v1(void) {
    for (;;) {
        uint8_t header[REQUEST_HEADER_BYTES];
        const int first = fgetc(stdin);
        if (first == EOF) {
            return ferror(stdin) ? fail_closed(FAILURE_INPUT) : 0;
        }
        header[0] = (uint8_t)first;
        Failure failure = read_remaining(header + 1, sizeof(header) - 1);
        if (failure != FAILURE_NONE) {
            if (failure == FAILURE_TRUNCATED_PAYLOAD) {
                failure = FAILURE_TRUNCATED_HEADER;
            }
            return fail_closed(failure);
        }

        Request request;
        memset(&request, 0, sizeof(request));
        failure = parse_header(header, &request);
        if (failure != FAILURE_NONE) return fail_closed(failure);

        uint8_t payload[CASE_PAYLOAD_BYTES];
        const size_t bytes = payload_length(&request);
        if (bytes > sizeof(payload)) return fail_closed(FAILURE_DENOMINATOR);
        failure = read_remaining(payload, bytes);
        if (failure != FAILURE_NONE) return fail_closed(failure);
        failure = parse_payload(&request, payload, bytes);
        if (failure != FAILURE_NONE) return fail_closed(failure);

        Interval interval;
        failure = calculate_interval(&request, &interval);
        if (failure != FAILURE_NONE) return fail_closed(failure);

        uint8_t response[RESPONSE_FRAME_BYTES];
        encode_response(&request, &interval, response);
        if (
            fwrite(response, 1, sizeof(response), stdout) != sizeof(response)
            || fflush(stdout) != 0
        ) {
            return fail_closed(FAILURE_OUTPUT);
        }
    }
}

static bool approximately_equal(double left, double right) {
    const double difference = fabs(left - right);
    const double scale = fmax(1.0, fmax(fabs(left), fabs(right)));
    return difference <= 1e-12 * scale;
}

static void build_synthetic_header(
    uint8_t header[REQUEST_HEADER_BYTES],
    uint16_t operation,
    uint64_t case_index
) {
    memset(header, 0, REQUEST_HEADER_BYTES);
    memcpy(header, REQUEST_MAGIC, sizeof(REQUEST_MAGIC));
    store_le16(header + 8, PROTOCOL_VERSION);
    store_le16(header + 10, operation);
    store_le32(header + 12, TRIALS);
    store_le32(header + 16, BOOTSTRAP_DRAWS);
    store_le32(header + 20, 1);
    for (size_t index = 0; index < SEED_BYTES; index++) {
        header[24 + index] = (uint8_t)(index + 1);
    }
    store_le64(header + 56, case_index);
}

static int self_test_failure(const char *name) {
    (void)fprintf(stderr, "rebar-bootstrap-v1: synthetic control failed: %s\n", name);
    return FAILURE_SELF_TEST;
}

#define SELF_CHECK(condition, name) \
    do { \
        if (!(condition)) return self_test_failure(name); \
        controls++; \
    } while (0)

static int self_test(void) {
    size_t controls = 0;
    uint8_t header[REQUEST_HEADER_BYTES];
    uint8_t changed[REQUEST_HEADER_BYTES];
    uint8_t payload[CASE_PAYLOAD_BYTES];
    uint8_t response[RESPONSE_FRAME_BYTES];
    uint8_t repeated[RESPONSE_FRAME_BYTES];
    Request request;

    build_synthetic_header(header, OP_CASE, 17);
    SELF_CHECK(parse_header(header, &request) == FAILURE_NONE, "canonical-case-header");
    SELF_CHECK(request.case_index == 17, "little-endian-case-index");
    SELF_CHECK(request.candidate == 1, "little-endian-candidate-index");
    SELF_CHECK(payload_length(&request) == CASE_PAYLOAD_BYTES, "case-payload-length");

    Xoshiro256 random;
    initialize_rng(&random, request.seed);
    static const uint64_t known_random[] = {
        UINT64_C(0x52bc258ef861cbe8),
        UINT64_C(0xbc258ef861cb3280),
        UINT64_C(0x2d013c0ee31e1c12),
        UINT64_C(0x2506e98014e9ac07),
        UINT64_C(0x62e739f7970c2cae),
        UINT64_C(0x6b67d55e63fe394d)
    };
    for (size_t index = 0; index < sizeof(known_random) / sizeof(known_random[0]); index++) {
        SELF_CHECK(next_random(&random) == known_random[index], "frozen-xoshiro256-star-star");
    }
    SELF_CHECK(
        (UINT64_C(0) - UINT64_C(19)) % UINT64_C(19) == 17,
        "unbiased-rejection-threshold"
    );

    for (size_t trial = 0; trial < TRIALS; trial++) {
        const uint64_t candidate = (uint64_t)trial + UINT64_C(1);
        store_le64(payload + trial * 16, candidate * UINT64_C(4));
        store_le64(payload + trial * 16 + 8, candidate);
    }
    SELF_CHECK(
        process_frame(header, payload, CASE_PAYLOAD_BYTES, response) == FAILURE_NONE,
        "positive-paired-case"
    );
    SELF_CHECK(
        process_frame(header, payload, CASE_PAYLOAD_BYTES, repeated) == FAILURE_NONE
        && memcmp(response, repeated, RESPONSE_FRAME_BYTES) == 0,
        "bitwise-deterministic-repeated-bootstrap"
    );
    SELF_CHECK(
        memcmp(response, RESPONSE_MAGIC, sizeof(RESPONSE_MAGIC)) == 0,
        "canonical-response-magic"
    );
    SELF_CHECK(
        memcmp(response + 8, header + 8, REQUEST_HEADER_BYTES - 8) == 0,
        "response-preserves-exact-request-metadata"
    );
    SELF_CHECK(
        approximately_equal(load_le_double(response + 64), 4.0)
        && approximately_equal(load_le_double(response + 72), 4.0)
        && approximately_equal(load_le_double(response + 80), 4.0),
        "constant-fourfold-paired-interval"
    );

    build_synthetic_header(changed, OP_AGGREGATE, UINT64_MAX);
    for (size_t trial = 0; trial < TRIALS; trial++) {
        store_le_double(payload + trial * 8, 0.0);
    }
    SELF_CHECK(
        process_frame(changed, payload, AGGREGATE_PAYLOAD_BYTES, response)
        == FAILURE_NONE,
        "finite-aggregate-header"
    );
    SELF_CHECK(
        approximately_equal(load_le_double(response + 64), 1.0)
        && approximately_equal(load_le_double(response + 72), 1.0)
        && approximately_equal(load_le_double(response + 80), 1.0),
        "unit-aggregate-geometric-interval"
    );

    memcpy(changed, header, sizeof(changed));
    changed[0] ^= 1;
    SELF_CHECK(parse_header(changed, &request) == FAILURE_REQUEST_MAGIC, "reject-foreign-magic");

    memcpy(changed, header, sizeof(changed));
    store_le16(changed + 8, 2);
    SELF_CHECK(parse_header(changed, &request) == FAILURE_VERSION, "reject-foreign-version");

    memcpy(changed, header, sizeof(changed));
    changed[8] = 0;
    changed[9] = 1;
    SELF_CHECK(parse_header(changed, &request) == FAILURE_VERSION, "reject-big-endian-version");

    memcpy(changed, header, sizeof(changed));
    store_le16(changed + 10, 3);
    SELF_CHECK(parse_header(changed, &request) == FAILURE_OPERATION, "reject-foreign-operation");

    memcpy(changed, header, sizeof(changed));
    store_le32(changed + 12, TRIALS - 1);
    SELF_CHECK(parse_header(changed, &request) == FAILURE_DENOMINATOR, "reject-trial-denominator");

    memcpy(changed, header, sizeof(changed));
    store_le32(changed + 16, BOOTSTRAP_DRAWS - 1);
    SELF_CHECK(parse_header(changed, &request) == FAILURE_DENOMINATOR, "reject-draw-denominator");

    memcpy(changed, header, sizeof(changed));
    store_le32(changed + 20, CANDIDATES);
    SELF_CHECK(parse_header(changed, &request) == FAILURE_CANDIDATE, "reject-candidate-index");

    memcpy(changed, header, sizeof(changed));
    memset(changed + 24, 0, SEED_BYTES);
    SELF_CHECK(parse_header(changed, &request) == FAILURE_SEED, "reject-zero-rng-state");

    memcpy(changed, header, sizeof(changed));
    store_le64(changed + 56, CASES);
    SELF_CHECK(parse_header(changed, &request) == FAILURE_CASE_INDEX, "reject-out-of-range-case");

    build_synthetic_header(changed, OP_AGGREGATE, 0);
    SELF_CHECK(parse_header(changed, &request) == FAILURE_CASE_INDEX, "reject-nonsentinel-aggregate");

    build_synthetic_header(changed, OP_AGGREGATE, UINT64_MAX);
    SELF_CHECK(parse_header(changed, &request) == FAILURE_NONE, "restore-aggregate-request");
    SELF_CHECK(
        parse_payload(&request, payload, AGGREGATE_PAYLOAD_BYTES - 1)
        == FAILURE_TRUNCATED_PAYLOAD,
        "reject-truncated-aggregate"
    );

    store_le64(payload, UINT64_C(0x7ff8000000000000));
    SELF_CHECK(
        parse_payload(&request, payload, AGGREGATE_PAYLOAD_BYTES)
        == FAILURE_NONFINITE_INPUT,
        "reject-nan-aggregate"
    );
    store_le64(payload, UINT64_C(0x7ff0000000000000));
    SELF_CHECK(
        parse_payload(&request, payload, AGGREGATE_PAYLOAD_BYTES)
        == FAILURE_NONFINITE_INPUT,
        "reject-positive-infinity"
    );
    store_le64(payload, UINT64_C(0xfff0000000000000));
    SELF_CHECK(
        parse_payload(&request, payload, AGGREGATE_PAYLOAD_BYTES)
        == FAILURE_NONFINITE_INPUT,
        "reject-negative-infinity"
    );

    for (size_t trial = 0; trial < TRIALS; trial++) {
        store_le_double(payload + trial * 8, DBL_MAX);
    }
    SELF_CHECK(
        process_frame(changed, payload, AGGREGATE_PAYLOAD_BYTES, response)
        == FAILURE_NONFINITE_STATISTIC,
        "reject-overflowing-aggregate"
    );

    SELF_CHECK(parse_header(header, &request) == FAILURE_NONE, "restore-case-request");
    SELF_CHECK(
        parse_payload(&request, payload, CASE_PAYLOAD_BYTES - 1)
        == FAILURE_TRUNCATED_PAYLOAD,
        "reject-truncated-paired-case"
    );
    memset(payload, 0, CASE_PAYLOAD_BYTES);
    SELF_CHECK(
        parse_payload(&request, payload, CASE_PAYLOAD_BYTES)
        == FAILURE_NONPOSITIVE_TIMING,
        "reject-zero-baseline-and-candidate"
    );
    for (size_t trial = 0; trial < TRIALS; trial++) {
        store_le64(payload + trial * 16, UINT64_MAX);
        store_le64(payload + trial * 16 + 8, UINT64_C(1));
    }
    SELF_CHECK(
        process_frame(header, payload, CASE_PAYLOAD_BYTES, response)
        == FAILURE_NONE
        && isfinite(load_le_double(response + 64))
        && isfinite(load_le_double(response + 72))
        && isfinite(load_le_double(response + 80)),
        "accept-largest-positive-uint64-pair"
    );

    (void)printf(
        "{\"schema\":\"rebar-postfinal-fresh-holdout-bootstrap-v1-self-test\","
        "\"status\":\"PASS\",\"candidate_imported\":false,"
        "\"holdout_accessed\":false,\"production_cases_materialized\":0,"
        "\"timing_performed\":false,\"trials\":%d,"
        "\"bootstrap_samples\":%d,\"lower_order_statistic\":%d,"
        "\"upper_order_statistic\":%d,\"request_header_bytes\":%d,"
        "\"response_frame_bytes\":%d,\"synthetic_controls\":%zu,"
        "\"failed\":0}\n",
        TRIALS,
        BOOTSTRAP_DRAWS,
        LOWER_ORDER_STATISTIC,
        UPPER_ORDER_STATISTIC,
        REQUEST_HEADER_BYTES,
        RESPONSE_FRAME_BYTES,
        controls
    );
    return 0;
}

#undef SELF_CHECK

int main(int argc, char **argv) {
    if (argc != 2) return fail_closed(FAILURE_USAGE);
    if (strcmp(argv[1], "--stream-v1") == 0) return stream_v1();
    if (strcmp(argv[1], "--self-test") == 0) return self_test();
    return fail_closed(FAILURE_USAGE);
}
