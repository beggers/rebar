from __future__ import annotations


class RecordingBenchmarkCompiledPattern:
    def __init__(self, calls: list[tuple[object, ...]]) -> None:
        self._calls = calls

    def search(self, haystack: object, *args: object, **kwargs: object) -> object:
        self._calls.append(("pattern.search", haystack, args, kwargs))
        return "pattern-result"

    def match(self, haystack: object, *args: object, **kwargs: object) -> object:
        self._calls.append(("pattern.match", haystack, args, kwargs))
        return "pattern-result"

    def fullmatch(
        self,
        haystack: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        self._calls.append(("pattern.fullmatch", haystack, args, kwargs))
        return "pattern-result"

    def split(self, haystack: object, *args: object, **kwargs: object) -> object:
        self._calls.append(("pattern.split", haystack, args, kwargs))
        return "pattern-result"

    def sub(
        self,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        self._calls.append(("pattern.sub", repl, string, args, kwargs))
        return "pattern-result"

    def subn(
        self,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        self._calls.append(("pattern.subn", repl, string, args, kwargs))
        return ("pattern-result", 0)


class RecordingBenchmarkModule:
    def __init__(
        self,
        *,
        helper_exception: Exception | None = None,
        compile_exception: Exception | None = None,
    ) -> None:
        self.calls: list[tuple[object, ...]] = []
        self._helper_exception = helper_exception
        self._compile_exception = compile_exception
        self.compiled_patterns: list[RecordingBenchmarkCompiledPattern] = []

    def _maybe_raise_helper_exception(self) -> None:
        if self._helper_exception is not None:
            raise self._helper_exception

    def purge(self) -> None:
        self.calls.append(("purge",))

    def compile(
        self,
        pattern: object,
        flags: int = 0,
    ) -> RecordingBenchmarkCompiledPattern:
        self.calls.append(("compile", pattern, flags))
        if isinstance(pattern, RecordingBenchmarkCompiledPattern):
            if self._compile_exception is not None:
                raise self._compile_exception
            return pattern
        compiled_pattern = RecordingBenchmarkCompiledPattern(self.calls)
        self.compiled_patterns.append(compiled_pattern)
        return compiled_pattern

    def search(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
        **kwargs: object,
    ) -> object:
        self.calls.append(("module.search", pattern, haystack, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def match(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
        **kwargs: object,
    ) -> object:
        self.calls.append(("module.match", pattern, haystack, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def fullmatch(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
        **kwargs: object,
    ) -> object:
        self.calls.append(("module.fullmatch", pattern, haystack, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def split(
        self,
        pattern: object,
        haystack: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        maxsplit = args[0] if args else 0
        flags = args[1] if len(args) > 1 else 0
        self.calls.append(("module.split", pattern, haystack, maxsplit, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def findall(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
    ) -> object:
        self.calls.append(("module.findall", pattern, haystack, flags))
        self._maybe_raise_helper_exception()
        return "module-result"

    def finditer(
        self,
        pattern: object,
        haystack: object,
        flags: int = 0,
    ) -> object:
        self.calls.append(("module.finditer", pattern, haystack, flags))
        self._maybe_raise_helper_exception()
        return iter(["module-finditer-result"])

    def sub(
        self,
        pattern: object,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        count = args[0] if args else 0
        flags = args[1] if len(args) > 1 else 0
        self.calls.append(("module.sub", pattern, repl, string, count, flags, kwargs))
        self._maybe_raise_helper_exception()
        return "module-result"

    def subn(
        self,
        pattern: object,
        repl: object,
        string: object,
        *args: object,
        **kwargs: object,
    ) -> object:
        count = args[0] if args else 0
        flags = args[1] if len(args) > 1 else 0
        self.calls.append(("module.subn", pattern, repl, string, count, flags, kwargs))
        self._maybe_raise_helper_exception()
        return ("module-result", 0)
