package main

/*
#include <stdint.h>

enum {
    REBAR_GO_ABI_V1 = 0x52424731,
    REBAR_GO_INPUT_BYTES = 0,
    REBAR_GO_INPUT_UNICODE_1 = 1,
    REBAR_GO_INPUT_UNICODE_2 = 2,
    REBAR_GO_INPUT_UNICODE_4 = 4,
    REBAR_GO_STATUS_OK = 0,
    REBAR_GO_STATUS_PATTERN = 1,
    REBAR_GO_STATUS_ARGUMENT = 2,
    REBAR_GO_STATUS_RUNTIME = 3,
    REBAR_GO_STATUS_HANDLE = 4
};

typedef struct {
    int32_t category;
    int64_t position;
    int64_t line;
    int64_t column;
    char message[256];
} rebar_go_status_v1;

typedef struct {
    int64_t *spans;
    uint64_t span_capacity;
    uint64_t capture_count;
    int64_t lastindex;
    uint32_t matched;
} rebar_go_match_v1;
*/
import "C"

import (
	"fmt"
	"runtime/cgo"
	"unsafe"
)

// Every exported operation is synchronous. Input pointers and span buffers
// remain owned by the C caller and are copied or filled before it returns.
// The only object retained across the boundary is an explicit cgo.Handle.

type bridgeIssue struct {
	category C.int32_t
	message  string
}

func (issue *bridgeIssue) Error() string {
	return issue.message
}

func setBridgeStatus(status *C.rebar_go_status_v1, failure error) {
	if status == nil {
		return
	}
	*status = C.rebar_go_status_v1{
		category: C.REBAR_GO_STATUS_RUNTIME,
		position: -1,
	}
	message := failure.Error()
	switch classified := failure.(type) {
	case *patternIssue:
		status.category = C.REBAR_GO_STATUS_PATTERN
		status.position = C.int64_t(classified.position)
		status.line = C.int64_t(classified.line)
		status.column = C.int64_t(classified.column)
		message = classified.message
	case *bridgeIssue:
		status.category = classified.category
		message = classified.message
	}
	destination := unsafe.Slice(
		(*byte)(unsafe.Pointer(&status.message[0])), len(status.message),
	)
	count := copy(destination[:len(destination)-1], []byte(message))
	destination[count] = 0
}

func guardedBridge(
	status *C.rebar_go_status_v1, operation func() error,
) (result C.int) {
	if status == nil {
		return -1
	}
	*status = C.rebar_go_status_v1{position: -1}
	result = 0
	defer func() {
		if recovered := recover(); recovered != nil {
			setBridgeStatus(status, &bridgeIssue{
				category: C.REBAR_GO_STATUS_RUNTIME,
				message: fmt.Sprintf(
					"owned Go engine recovered a runtime panic: %v", recovered,
				),
			})
			result = -1
		}
	}()
	if failure := operation(); failure != nil {
		setBridgeStatus(status, failure)
		return -1
	}
	return 0
}

func argumentFailure(message string) error {
	return &bridgeIssue{
		category: C.REBAR_GO_STATUS_ARGUMENT, message: message,
	}
}

func handleFailure(message string) error {
	return &bridgeIssue{
		category: C.REBAR_GO_STATUS_HANDLE, message: message,
	}
}

func decodeBridgeInput(
	kind C.uint32_t, pointer unsafe.Pointer, length C.uint64_t,
) ([]rune, inputDomain, error) {
	if uint64(length) > uint64(^uint(0)>>1) {
		return nil, bytesDomain, argumentFailure(
			"input length exceeds the native Go addressable range",
		)
	}
	count := int(length)
	if count != 0 && pointer == nil {
		return nil, bytesDomain, argumentFailure(
			"nonempty input has a null data pointer",
		)
	}
	units := make([]rune, count)
	switch kind {
	case C.REBAR_GO_INPUT_BYTES:
		for index, value := range unsafe.Slice((*byte)(pointer), count) {
			units[index] = rune(value)
		}
		return units, bytesDomain, nil
	case C.REBAR_GO_INPUT_UNICODE_1:
		for index, value := range unsafe.Slice((*uint8)(pointer), count) {
			units[index] = rune(value)
		}
	case C.REBAR_GO_INPUT_UNICODE_2:
		for index, value := range unsafe.Slice((*uint16)(pointer), count) {
			units[index] = rune(value)
		}
	case C.REBAR_GO_INPUT_UNICODE_4:
		for index, value := range unsafe.Slice((*uint32)(pointer), count) {
			if value > 0x10ffff {
				return nil, textDomain, argumentFailure(
					"input contains a code point outside the Unicode range",
				)
			}
			units[index] = rune(value)
		}
	default:
		return nil, bytesDomain, argumentFailure(
			"unrecognized CPython Unicode storage or bytes input kind",
		)
	}
	return units, textDomain, nil
}

func lookupCompiled(raw C.uintptr_t) (
	compiled *compiledExpression, failure error,
) {
	if raw == 0 {
		return nil, handleFailure("regular-expression handle is closed")
	}
	defer func() {
		if recover() != nil {
			compiled = nil
			failure = handleFailure(
				"regular-expression handle is stale or belongs to another runtime",
			)
		}
	}()
	value := cgo.Handle(uintptr(raw)).Value()
	compiled, valid := value.(*compiledExpression)
	if !valid || compiled == nil {
		return nil, handleFailure(
			"runtime handle does not identify an owned Go compiled expression",
		)
	}
	return compiled, nil
}

//export rebar_go_abi_version
func rebar_go_abi_version() C.uint32_t {
	return C.REBAR_GO_ABI_V1
}

//export rebar_go_compile
func rebar_go_compile(
	kind C.uint32_t,
	pointer unsafe.Pointer,
	length C.uint64_t,
	flags C.uint32_t,
	out *C.uintptr_t,
	status *C.rebar_go_status_v1,
) C.int {
	return guardedBridge(status, func() error {
		if out == nil {
			return argumentFailure("compile requires an output handle")
		}
		*out = 0
		pattern, domain, err := decodeBridgeInput(kind, pointer, length)
		if err != nil {
			return err
		}
		compiled, err := compileExpression(pattern, domain, uint32(flags))
		if err != nil {
			return err
		}
		*out = C.uintptr_t(uintptr(cgo.NewHandle(compiled)))
		return nil
	})
}

//export rebar_go_metadata
func rebar_go_metadata(
	raw C.uintptr_t,
	flags *C.uint32_t,
	groups *C.uint64_t,
	status *C.rebar_go_status_v1,
) C.int {
	return guardedBridge(status, func() error {
		if flags == nil || groups == nil {
			return argumentFailure("metadata requires both output pointers")
		}
		compiled, err := lookupCompiled(raw)
		if err != nil {
			return err
		}
		*flags = C.uint32_t(compiled.flags)
		*groups = C.uint64_t(compiled.groupCount)
		return nil
	})
}

//export rebar_go_group_name
func rebar_go_group_name(
	raw C.uintptr_t,
	index C.uint64_t,
	destination unsafe.Pointer,
	capacity C.uint64_t,
	required *C.uint64_t,
	status *C.rebar_go_status_v1,
) C.int {
	return guardedBridge(status, func() error {
		if required == nil {
			return argumentFailure("group-name lookup requires a size output")
		}
		*required = 0
		compiled, err := lookupCompiled(raw)
		if err != nil {
			return err
		}
		if index == 0 || uint64(index) > uint64(compiled.groupCount) {
			return argumentFailure("group-name index is outside the compiled pattern")
		}
		name := compiled.groupNames[int(index)-1]
		if name == "" {
			return nil
		}
		encoded := []byte(name)
		*required = C.uint64_t(uint64(len(encoded)) + 1)
		if destination == nil && capacity == 0 {
			return nil
		}
		if destination == nil || uint64(capacity) < uint64(len(encoded))+1 ||
			uint64(capacity) > uint64(^uint(0)>>1) {
			return argumentFailure("group-name destination is null or too small")
		}
		buffer := unsafe.Slice((*byte)(destination), int(capacity))
		copy(buffer, encoded)
		buffer[len(encoded)] = 0
		return nil
	})
}

func fillMatchResult(
	compiled *compiledExpression,
	found *traversalState,
	result *C.rebar_go_match_v1,
) error {
	if result == nil {
		return argumentFailure("matching requires a result structure")
	}
	result.matched = 0
	result.capture_count = C.uint64_t(compiled.groupCount + 1)
	result.lastindex = -1
	if found == nil {
		return nil
	}
	needed := uint64(compiled.groupCount + 1)
	if result.spans == nil || uint64(result.span_capacity) < needed ||
		needed > uint64(^uint(0)>>1)/2 {
		return argumentFailure("capture-span output is null or too small")
	}
	output := unsafe.Slice(
		(*int64)(unsafe.Pointer(result.spans)), int(needed)*2,
	)
	for index, span := range found.spans {
		output[index*2] = int64(span.start)
		output[index*2+1] = int64(span.end)
	}
	result.lastindex = C.int64_t(found.last)
	result.matched = 1
	return nil
}

func bridgeMatch(
	raw C.uintptr_t,
	kind C.uint32_t,
	pointer unsafe.Pointer,
	length C.uint64_t,
	start C.int64_t,
	end C.int64_t,
	rejectEmpty C.uint32_t,
	searching bool,
	full bool,
	result *C.rebar_go_match_v1,
	status *C.rebar_go_status_v1,
) C.int {
	return guardedBridge(status, func() error {
		if result == nil {
			return argumentFailure("matching requires a result structure")
		}
		compiled, err := lookupCompiled(raw)
		if err != nil {
			return err
		}
		subject, domain, err := decodeBridgeInput(kind, pointer, length)
		if err != nil {
			return err
		}
		if domain != compiled.domain {
			return argumentFailure(
				"pattern and subject must both be text or both be bytes",
			)
		}
		maximum := int64(^uint(0) >> 1)
		if start > maximum || end > maximum {
			return argumentFailure("matching window exceeds the native addressable range")
		}
		found, err := compiled.firstMatch(
			subject, int(start), int(end), searching, full, rejectEmpty != 0,
		)
		if err != nil {
			return err
		}
		return fillMatchResult(compiled, found, result)
	})
}

//export rebar_go_match_at
func rebar_go_match_at(
	raw C.uintptr_t,
	kind C.uint32_t,
	pointer unsafe.Pointer,
	length C.uint64_t,
	start C.int64_t,
	end C.int64_t,
	rejectEmpty C.uint32_t,
	result *C.rebar_go_match_v1,
	status *C.rebar_go_status_v1,
) C.int {
	return bridgeMatch(
		raw, kind, pointer, length, start, end, rejectEmpty,
		false, false, result, status,
	)
}

//export rebar_go_search
func rebar_go_search(
	raw C.uintptr_t,
	kind C.uint32_t,
	pointer unsafe.Pointer,
	length C.uint64_t,
	start C.int64_t,
	end C.int64_t,
	rejectEmpty C.uint32_t,
	result *C.rebar_go_match_v1,
	status *C.rebar_go_status_v1,
) C.int {
	return bridgeMatch(
		raw, kind, pointer, length, start, end, rejectEmpty,
		true, false, result, status,
	)
}

//export rebar_go_fullmatch
func rebar_go_fullmatch(
	raw C.uintptr_t,
	kind C.uint32_t,
	pointer unsafe.Pointer,
	length C.uint64_t,
	start C.int64_t,
	end C.int64_t,
	result *C.rebar_go_match_v1,
	status *C.rebar_go_status_v1,
) C.int {
	return bridgeMatch(
		raw, kind, pointer, length, start, end, 0,
		false, true, result, status,
	)
}

//export rebar_go_release
func rebar_go_release(
	raw C.uintptr_t, status *C.rebar_go_status_v1,
) C.int {
	return guardedBridge(status, func() error {
		if _, err := lookupCompiled(raw); err != nil {
			return err
		}
		cgo.Handle(uintptr(raw)).Delete()
		return nil
	})
}

// A main package is required by Go's c-shared build mode. This experiment is
// source-only: no shared library has been built or loaded.
func main() {}
