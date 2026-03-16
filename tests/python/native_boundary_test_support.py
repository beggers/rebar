from __future__ import annotations

import rebar


class RecordingNativeBoundary:
    def __init__(self, *, native_placeholder_messages: bool = False) -> None:
        self.calls: list[tuple[object, ...]] = []
        self._native_placeholder_messages = native_placeholder_messages

    def _dispatch(
        self,
        recorded_call: tuple[object, ...],
        handler_name: str,
        *handler_args: object,
    ) -> object:
        self.calls.append(recorded_call)
        try:
            handler = getattr(self, handler_name)
        except AttributeError as exc:
            raise AssertionError(f"unexpected {recorded_call[0]} call") from exc
        return handler(*handler_args)

    def boundary_compile(self, pattern: str | bytes, flags: int) -> tuple[str, int, bool]:
        return self._dispatch(("compile", pattern, flags), "compile_result", pattern, flags)

    def boundary_literal_match(
        self,
        pattern: str | bytes,
        flags: int,
        mode: str,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, tuple[int, int] | None]:
        return self._dispatch(
            ("match", pattern, flags, mode, string, pos, endpos),
            "literal_match_result",
            pattern,
            flags,
            mode,
            string,
            pos,
            endpos,
        )

    def boundary_literal_split(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        maxsplit: int,
    ) -> tuple[str, list[str] | list[bytes] | None]:
        return self._dispatch(
            ("split", pattern, flags, string, maxsplit),
            "literal_split_result",
            pattern,
            flags,
            string,
            maxsplit,
        )

    def boundary_literal_findall(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, list[str] | list[bytes] | None]:
        return self._dispatch(
            ("findall", pattern, flags, string, pos, endpos),
            "literal_findall_result",
            pattern,
            flags,
            string,
            pos,
            endpos,
        )

    def boundary_literal_finditer(
        self,
        pattern: str | bytes,
        flags: int,
        string: str | bytes,
        pos: int,
        endpos: int | None,
    ) -> tuple[str, int, int, list[tuple[int, int]]]:
        return self._dispatch(
            ("finditer", pattern, flags, string, pos, endpos),
            "literal_finditer_result",
            pattern,
            flags,
            string,
            pos,
            endpos,
        )

    def boundary_literal_subn(
        self,
        pattern: str | bytes,
        flags: int,
        repl: str | bytes,
        string: str | bytes,
        count: int,
    ) -> tuple[str, str | bytes | None, int]:
        return self._dispatch(
            ("subn", pattern, flags, repl, string, count),
            "literal_subn_result",
            pattern,
            flags,
            repl,
            string,
            count,
        )

    def boundary_escape(self, pattern: str | bytes) -> str | bytes:
        return self._dispatch(("escape", pattern), "escape_result", pattern)

    def scaffold_raise(self, helper_name: str) -> object:
        if self._native_placeholder_messages:
            raise NotImplementedError(f"native helper placeholder {helper_name}")
        raise NotImplementedError(rebar._placeholder_message(helper_name))

    def scaffold_pattern_raise(self, method_name: str) -> object:
        if self._native_placeholder_messages:
            raise NotImplementedError(f"native pattern placeholder {method_name}")
        raise NotImplementedError(rebar._pattern_placeholder_message(method_name))

    def scaffold_purge(self) -> None:
        self.calls.append(("purge",))
