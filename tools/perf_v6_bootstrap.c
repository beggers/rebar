#include <math.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>

/* The same MT19937 initialization and four-bit rejection draw used by
 * random.Random(seed).randrange(13).  Keeping this small and dependency-free
 * makes the large, paired bootstrap practical without changing its samples. */
static uint32_t state[624];
static size_t state_index = 624;

void rebar_bootstrap_seed(uint32_t seed) {
    state[0] = 19650218U;
    for (size_t i = 1; i < 624; i++) {
        state[i] = 1812433253U * (state[i - 1] ^ (state[i - 1] >> 30)) + (uint32_t)i;
    }
    size_t i = 1;
    size_t j = 0;
    for (size_t remaining = 624; remaining != 0; remaining--) {
        state[i] = (state[i] ^ ((state[i - 1] ^ (state[i - 1] >> 30)) * 1664525U)) + seed + (uint32_t)j;
        i++;
        j++;
        if (i >= 624) {
            state[0] = state[623];
            i = 1;
        }
        if (j >= 1) j = 0;
    }
    for (size_t remaining = 623; remaining != 0; remaining--) {
        state[i] = (state[i] ^ ((state[i - 1] ^ (state[i - 1] >> 30)) * 1566083941U)) - (uint32_t)i;
        i++;
        if (i >= 624) {
            state[0] = state[623];
            i = 1;
        }
    }
    state[0] = 0x80000000U;
    state_index = 624;
}

static uint32_t next_u32(void) {
    if (state_index >= 624) {
        for (size_t i = 0; i < 624; i++) {
            uint32_t value = (state[i] & 0x80000000U) | (state[(i + 1) % 624] & 0x7fffffffU);
            state[i] = state[(i + 397) % 624] ^ (value >> 1) ^ ((value & 1U) ? 0x9908b0dfU : 0U);
        }
        state_index = 0;
    }
    uint32_t value = state[state_index++];
    value ^= value >> 11;
    value ^= (value << 7) & 0x9d2c5680U;
    value ^= (value << 15) & 0xefc60000U;
    value ^= value >> 18;
    return value;
}

static uint32_t draw13(void) {
    uint32_t value;
    do {
        value = next_u32() >> 28;
    } while (value >= 13U);
    return value;
}

void rebar_bootstrap_draws(uint32_t *output, size_t count) {
    for (size_t i = 0; i < count; i++) output[i] = draw13();
}

static double selected(double *values, size_t count, size_t wanted) {
    size_t left = 0;
    size_t right = count;
    while (right - left > 1) {
        double pivot = values[left + (right - left) / 2];
        size_t lower = left;
        size_t cursor = left;
        size_t upper = right;
        while (cursor < upper) {
            if (values[cursor] < pivot) {
                double swap = values[lower];
                values[lower++] = values[cursor];
                values[cursor++] = swap;
            } else if (values[cursor] > pivot) {
                double swap = values[--upper];
                values[upper] = values[cursor];
                values[cursor] = swap;
            } else {
                cursor++;
            }
        }
        if (wanted < lower) right = lower;
        else if (wanted >= upper) left = upper;
        else return values[wanted];
    }
    return values[wanted];
}

static void bounds(double *samples, size_t count, double *low, double *high) {
    size_t low_index = (size_t)floor(.025 * (double)(count - 1));
    size_t high_index = (size_t)floor(.975 * (double)(count - 1));
    *low = exp(selected(samples, count, low_index));
    *high = exp(selected(samples, count, high_index));
}

int rebar_bootstrap_cases(const double *logs, size_t results, size_t trials, size_t bootstraps, double *lows, double *highs) {
    if (trials != 13 || bootstraps == 0) return -1;
    double *samples = malloc(bootstraps * sizeof(*samples));
    if (samples == NULL) return -1;
    for (size_t result = 0; result < results; result++) {
        const double *values = logs + result * trials;
        for (size_t sample = 0; sample < bootstraps; sample++) {
            double total = 0;
            for (size_t draw = 0; draw < trials; draw++) total += values[draw13()];
            samples[sample] = total / (double)trials;
        }
        bounds(samples, bootstraps, &lows[result], &highs[result]);
    }
    free(samples);
    return 0;
}

int rebar_bootstrap_overall(const double *logs, const uint32_t *cases, const double *weights, size_t selected_cases, size_t candidates, size_t candidate, size_t trials, size_t bootstraps, double denominator, double *low, double *high) {
    if (trials != 13 || bootstraps == 0 || candidate >= candidates || denominator <= 0) return -1;
    double *samples = malloc(bootstraps * sizeof(*samples));
    if (samples == NULL) return -1;
    for (size_t sample = 0; sample < bootstraps; sample++) {
        double total = 0;
        for (size_t item = 0; item < selected_cases; item++) {
            const double *values = logs + (((size_t)cases[item] * candidates + candidate) * trials);
            double mean = 0;
            for (size_t draw = 0; draw < trials; draw++) mean += values[draw13()];
            total += mean / (double)trials * weights[item];
        }
        samples[sample] = total / denominator;
    }
    bounds(samples, bootstraps, low, high);
    free(samples);
    return 0;
}
