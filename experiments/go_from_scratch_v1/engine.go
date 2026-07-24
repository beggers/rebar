package main

import (
	"fmt"
	"strings"
	"unicode"
)

// This is an independently authored experimental regular-expression engine.
// In particular, no package from regexp, regexp/syntax, another candidate, or
// a third-party matching engine participates in lexing, parsing, or matching.

const (
	flagIgnoreCase uint32 = 2
	flagLocale     uint32 = 4
	flagMultiline  uint32 = 8
	flagDotAll     uint32 = 16
	flagUnicode    uint32 = 32
	flagVerbose    uint32 = 64
	flagDebug      uint32 = 128
	flagASCII      uint32 = 256
	knownFlags            = flagIgnoreCase | flagLocale | flagMultiline |
		flagDotAll | flagUnicode | flagVerbose | flagDebug | flagASCII
	maxRepeat uint64 = 1<<32 - 1
)

type inputDomain uint8

const (
	bytesDomain inputDomain = iota
	textDomain
)

type patternIssue struct {
	message  string
	position int
	line     int
	column   int
}

func (issue *patternIssue) Error() string {
	if issue.position < 0 {
		return issue.message
	}
	message := fmt.Sprintf("%s at position %d", issue.message, issue.position)
	if issue.line > 1 {
		message += fmt.Sprintf(" (line %d, column %d)", issue.line, issue.column)
	}
	return message
}

func issueAt(pattern []rune, position int, message string) *patternIssue {
	if position < 0 {
		return &patternIssue{message: message, position: -1}
	}
	if position > len(pattern) {
		position = len(pattern)
	}
	line, column := 1, 1
	for _, value := range pattern[:position] {
		if value == '\n' {
			line++
			column = 1
		} else {
			column++
		}
	}
	return &patternIssue{
		message: message, position: position, line: line, column: column,
	}
}

type lexicalKind uint8

const (
	plainToken lexicalKind = iota
	quotedToken
	operatorEscapeToken
	numberEscapeToken
	endToken
)

type lexicalToken struct {
	kind     lexicalKind
	value    rune
	position int
	spelling string
}

func hexadecimalDigit(value rune) (uint32, bool) {
	switch {
	case value >= '0' && value <= '9':
		return uint32(value - '0'), true
	case value >= 'a' && value <= 'f':
		return uint32(value-'a') + 10, true
	case value >= 'A' && value <= 'F':
		return uint32(value-'A') + 10, true
	default:
		return 0, false
	}
}

func lexPattern(pattern []rune, domain inputDomain) ([]lexicalToken, error) {
	tokens := make([]lexicalToken, 0, len(pattern)+1)
	for index := 0; index < len(pattern); {
		position := index
		value := pattern[index]
		index++
		if value != '\\' {
			tokens = append(tokens, lexicalToken{
				kind: plainToken, value: value, position: position,
			})
			continue
		}
		if index == len(pattern) {
			return nil, issueAt(pattern, position, "bad escape (end of pattern)")
		}
		value = pattern[index]
		index++
		switch value {
		case 'a', 'f', 'n', 'r', 't', 'v':
			decoded := map[rune]rune{
				'a': '\a', 'f': '\f', 'n': '\n',
				'r': '\r', 't': '\t', 'v': '\v',
			}[value]
			tokens = append(tokens, lexicalToken{
				kind: quotedToken, value: decoded, position: position,
				spelling: string(pattern[position:index]),
			})
		case 'd', 'D', 's', 'S', 'w', 'W', 'b', 'B', 'A', 'Z', 'z':
			tokens = append(tokens, lexicalToken{
				kind: operatorEscapeToken, value: value, position: position,
				spelling: string(pattern[position:index]),
			})
		case 'x', 'u', 'U':
			width := 2
			if value == 'u' {
				width = 4
			} else if value == 'U' {
				width = 8
			}
			if domain == bytesDomain && value != 'x' {
				return nil, issueAt(pattern, position,
					fmt.Sprintf("bad escape \\%c", value))
			}
			if len(pattern)-index < width {
				return nil, issueAt(pattern, position,
					fmt.Sprintf("incomplete escape \\%c", value))
			}
			var decoded uint32
			for offset := 0; offset < width; offset++ {
				digit, valid := hexadecimalDigit(pattern[index+offset])
				if !valid {
					return nil, issueAt(pattern, position,
						fmt.Sprintf("incomplete escape \\%c", value))
				}
				decoded = decoded*16 + digit
			}
			if decoded > unicode.MaxRune {
				return nil, issueAt(pattern, position, "bad escape (invalid Unicode character)")
			}
			index += width
			tokens = append(tokens, lexicalToken{
				kind: quotedToken, value: rune(decoded), position: position,
				spelling: string(pattern[position:index]),
			})
		case 'N':
			return nil, issueAt(pattern, position,
				"Unicode character-name escapes are not implemented by the Go experiment")
		default:
			if value >= '0' && value <= '9' {
				if value == '0' {
					for consumed := 1; consumed < 3 && index < len(pattern); consumed++ {
						if pattern[index] < '0' || pattern[index] > '7' {
							break
						}
						index++
					}
				} else if value <= '7' && index+1 < len(pattern) &&
					pattern[index] >= '0' && pattern[index] <= '7' &&
					pattern[index+1] >= '0' && pattern[index+1] <= '7' {
					index += 2
				} else if index < len(pattern) &&
					pattern[index] >= '0' && pattern[index] <= '9' {
					index++
				}
				tokens = append(tokens, lexicalToken{
					kind: numberEscapeToken, value: value, position: position,
					spelling: string(pattern[position:index]),
				})
				continue
			}
			if (value >= 'a' && value <= 'z') ||
				(value >= 'A' && value <= 'Z') {
				return nil, issueAt(pattern, position,
					fmt.Sprintf("bad escape \\%c", value))
			}
			tokens = append(tokens, lexicalToken{
				kind: quotedToken, value: value, position: position,
				spelling: string(pattern[position:index]),
			})
		}
	}
	tokens = append(tokens, lexicalToken{
		kind: endToken, position: len(pattern),
	})
	return tokens, nil
}

type expressionKind uint8

const (
	emptyExpression expressionKind = iota
	literalExpression
	sequenceExpression
	alternativeExpression
	classExpression
	dotExpression
	categoryExpression
	anchorExpression
	boundaryExpression
	captureExpression
	backreferenceExpression
	repetitionExpression
	lookaheadExpression
	lookbehindExpression
	atomicExpression
	conditionalExpression
	inlineFlagExpression
)

type classTerm struct {
	low      rune
	high     rune
	category rune
}

type expression struct {
	kind       expressionKind
	flags      uint32
	value      rune
	children   []*expression
	terms      []classTerm
	group      int
	minimum    int
	maximum    int
	width      int
	negative   bool
	lazy       bool
	possessive bool
}

type independentParser struct {
	pattern    []rune
	tokens     []lexicalToken
	domain     inputDomain
	index      int
	groups     int
	groupNames []string
	nameIndex  map[string]int
	openGroups map[int]bool
	rootFlags  uint32
	depth      int
	rootAtoms  int
}

func (parser *independentParser) current() lexicalToken {
	if parser.index >= len(parser.tokens) {
		return lexicalToken{kind: endToken, position: len(parser.pattern)}
	}
	return parser.tokens[parser.index]
}

func (parser *independentParser) plain(value rune) bool {
	token := parser.current()
	return token.kind == plainToken && token.value == value
}

func (parser *independentParser) takePlain(value rune) bool {
	if !parser.plain(value) {
		return false
	}
	parser.index++
	return true
}

func (parser *independentParser) skipVerbose(flags uint32) {
	if flags&flagVerbose == 0 {
		return
	}
	for {
		token := parser.current()
		if token.kind != plainToken {
			return
		}
		if strings.ContainsRune(" \t\n\r\v\f", token.value) {
			parser.index++
			continue
		}
		if token.value != '#' {
			return
		}
		for parser.current().kind != endToken {
			value := parser.current().value
			parser.index++
			if value == '\n' {
				break
			}
		}
	}
}

func (parser *independentParser) fail(position int, message string) error {
	return issueAt(parser.pattern, position, message)
}

func decimalRunes(values []rune) (uint64, bool) {
	if len(values) == 0 {
		return 0, false
	}
	var result uint64
	for _, value := range values {
		if value < '0' || value > '9' {
			return 0, false
		}
		digit := uint64(value - '0')
		if result > (^uint64(0)-digit)/10 {
			return 0, false
		}
		result = result*10 + digit
	}
	return result, true
}

func (parser *independentParser) parse(flags uint32) (*expression, error) {
	active := flags
	node, err := parser.alternation(&active)
	if err != nil {
		return nil, err
	}
	parser.skipVerbose(active)
	if parser.current().kind != endToken {
		return nil, parser.fail(parser.current().position, "unbalanced parenthesis")
	}
	parser.rootFlags = active
	return node, nil
}

func sequenceOf(children []*expression, flags uint32) *expression {
	if len(children) == 0 {
		return &expression{kind: emptyExpression, flags: flags}
	}
	if len(children) == 1 {
		return children[0]
	}
	return &expression{kind: sequenceExpression, flags: flags, children: children}
}

func (parser *independentParser) alternation(flags *uint32) (*expression, error) {
	first, err := parser.sequence(flags)
	if err != nil {
		return nil, err
	}
	branches := []*expression{first}
	for parser.takePlain('|') {
		branch, parseError := parser.sequence(flags)
		if parseError != nil {
			return nil, parseError
		}
		branches = append(branches, branch)
	}
	if len(branches) == 1 {
		return first, nil
	}
	return &expression{
		kind: alternativeExpression, flags: *flags, children: branches,
	}, nil
}

func (parser *independentParser) sequence(flags *uint32) (*expression, error) {
	children := make([]*expression, 0)
	for {
		parser.skipVerbose(*flags)
		token := parser.current()
		if token.kind == endToken || parser.plain('|') || parser.plain(')') {
			return sequenceOf(children, *flags), nil
		}
		node, err := parser.atom(*flags)
		if err != nil {
			return nil, err
		}
		if node.kind == inlineFlagExpression {
			if parser.depth != 0 || parser.rootAtoms != 0 || len(children) != 0 {
				return nil, parser.fail(token.position,
					"global flags not at the start of the expression")
			}
			*flags = node.flags
			parser.rootFlags = node.flags
			continue
		}
		parser.skipVerbose(*flags)
		node, err = parser.quantify(node, *flags)
		if err != nil {
			return nil, err
		}
		children = append(children, node)
		if parser.depth == 0 {
			parser.rootAtoms++
		}
	}
}

func (parser *independentParser) atom(flags uint32) (*expression, error) {
	token := parser.current()
	parser.index++
	switch token.kind {
	case quotedToken:
		return &expression{
			kind: literalExpression, flags: flags, value: token.value,
		}, nil
	case numberEscapeToken:
		return parser.numberEscape(token, flags, false)
	case operatorEscapeToken:
		switch token.value {
		case 'd', 'D', 's', 'S', 'w', 'W':
			return &expression{
				kind: categoryExpression, flags: flags, value: token.value,
			}, nil
		case 'b', 'B':
			return &expression{
				kind: boundaryExpression, flags: flags,
				negative: token.value == 'B',
			}, nil
		case 'A', 'Z', 'z':
			return &expression{
				kind: anchorExpression, flags: flags, value: token.value,
			}, nil
		}
	case plainToken:
		switch token.value {
		case '.':
			return &expression{kind: dotExpression, flags: flags}, nil
		case '^', '$':
			return &expression{
				kind: anchorExpression, flags: flags, value: token.value,
			}, nil
		case '[':
			return parser.characterClass(token.position, flags)
		case '(':
			return parser.group(token.position, flags)
		case '*', '+', '?':
			return nil, parser.fail(token.position, "nothing to repeat")
		default:
			return &expression{
				kind: literalExpression, flags: flags, value: token.value,
			}, nil
		}
	}
	return nil, parser.fail(token.position, "unexpected end of pattern")
}

func (parser *independentParser) numberEscape(
	token lexicalToken, flags uint32, insideClass bool,
) (*expression, error) {
	digits := []rune(strings.TrimPrefix(token.spelling, "\\"))
	octal := insideClass || digits[0] == '0' || len(digits) == 3
	if octal {
		var value uint64
		for _, digit := range digits {
			if digit < '0' || digit > '7' {
				return nil, parser.fail(token.position,
					fmt.Sprintf("bad escape %s", token.spelling))
			}
			value = value*8 + uint64(digit-'0')
		}
		if value > 0xff {
			return nil, parser.fail(token.position,
				fmt.Sprintf("octal escape value %s outside of range 0-0o377",
					token.spelling))
		}
		return &expression{
			kind: literalExpression, flags: flags, value: rune(value),
		}, nil
	}
	value, valid := decimalRunes(digits)
	if !valid || value == 0 || value > uint64(parser.groups) {
		return nil, parser.fail(token.position+1,
			fmt.Sprintf("invalid group reference %s", string(digits)))
	}
	if parser.openGroups[int(value)] {
		return nil, parser.fail(token.position, "cannot refer to an open group")
	}
	return &expression{
		kind: backreferenceExpression, flags: flags, group: int(value),
	}, nil
}

func (parser *independentParser) classAtom() (classTerm, bool, error) {
	token := parser.current()
	if token.kind == endToken {
		return classTerm{}, false,
			parser.fail(token.position, "unterminated character set")
	}
	parser.index++
	switch token.kind {
	case plainToken, quotedToken:
		return classTerm{low: token.value, high: token.value}, true, nil
	case operatorEscapeToken:
		if token.value == 'b' {
			return classTerm{low: '\b', high: '\b'}, true, nil
		}
		if strings.ContainsRune("dDsSwW", token.value) {
			return classTerm{category: token.value}, false, nil
		}
		return classTerm{}, false, parser.fail(token.position,
			fmt.Sprintf("bad escape %s", token.spelling))
	case numberEscapeToken:
		node, err := parser.numberEscape(token, 0, true)
		if err != nil {
			return classTerm{}, false, err
		}
		return classTerm{low: node.value, high: node.value}, true, nil
	default:
		return classTerm{}, false,
			parser.fail(token.position, "unterminated character set")
	}
}

func (parser *independentParser) characterClass(
	position int, flags uint32,
) (*expression, error) {
	negative := parser.takePlain('^')
	terms := make([]classTerm, 0)
	first := true
	for {
		if parser.current().kind == endToken {
			return nil, parser.fail(position, "unterminated character set")
		}
		if parser.plain(']') && !first {
			parser.index++
			return &expression{
				kind: classExpression, flags: flags,
				terms: terms, negative: negative,
			}, nil
		}
		first = false
		leftPosition := parser.current().position
		left, literal, err := parser.classAtom()
		if err != nil {
			return nil, err
		}
		if parser.plain('-') && parser.index+1 < len(parser.tokens) &&
			!(parser.tokens[parser.index+1].kind == plainToken &&
				parser.tokens[parser.index+1].value == ']') {
			parser.index++
			right, rightLiteral, rangeError := parser.classAtom()
			if rangeError != nil {
				return nil, rangeError
			}
			if !literal || !rightLiteral || left.low > right.low {
				return nil, parser.fail(leftPosition, "bad character range")
			}
			left.high = right.low
		}
		terms = append(terms, left)
	}
}

func identifierStart(value rune) bool {
	return value == '_' || unicode.IsLetter(value) || unicode.Is(unicode.Nl, value)
}

func identifierContinue(value rune) bool {
	return identifierStart(value) || unicode.IsDigit(value) ||
		unicode.Is(unicode.Mn, value) || unicode.Is(unicode.Mc, value) ||
		unicode.Is(unicode.Pc, value)
}

func (parser *independentParser) readGroupName(end rune) (string, int, error) {
	start := parser.current().position
	values := make([]rune, 0)
	for parser.current().kind != endToken && !parser.plain(end) {
		token := parser.current()
		if token.kind != plainToken ||
			(len(values) == 0 && !identifierStart(token.value)) ||
			(len(values) != 0 && !identifierContinue(token.value)) ||
			(parser.domain == bytesDomain && token.value > unicode.MaxASCII) {
			return "", start, parser.fail(start, "bad character in group name")
		}
		values = append(values, token.value)
		parser.index++
	}
	if len(values) == 0 {
		return "", start, parser.fail(start, "missing group name")
	}
	if !parser.takePlain(end) {
		return "", start, parser.fail(start, "unterminated group name")
	}
	return string(values), start, nil
}

func (parser *independentParser) childGroup(flags uint32, opening int) (*expression, error) {
	parser.depth++
	active := flags
	node, err := parser.alternation(&active)
	parser.depth--
	if err != nil {
		return nil, err
	}
	if !parser.takePlain(')') {
		return nil, parser.fail(opening, "missing ), unterminated subpattern")
	}
	return node, nil
}

func inlineFlag(value rune) (uint32, bool) {
	switch value {
	case 'a':
		return flagASCII, true
	case 'i':
		return flagIgnoreCase, true
	case 'L':
		return flagLocale, true
	case 'm':
		return flagMultiline, true
	case 's':
		return flagDotAll, true
	case 'u':
		return flagUnicode, true
	case 'x':
		return flagVerbose, true
	default:
		return 0, false
	}
}

func (parser *independentParser) flagGroup(
	position int, current uint32,
) (*expression, error) {
	var enable, disable uint32
	negative := false
	for {
		token := parser.current()
		if token.kind == endToken {
			return nil, parser.fail(position, "missing -, : or )")
		}
		if parser.plain(':') || parser.plain(')') {
			break
		}
		if parser.takePlain('-') {
			if negative {
				return nil, parser.fail(token.position, "missing flag")
			}
			negative = true
			continue
		}
		if token.kind != plainToken {
			return nil, parser.fail(token.position, "unknown flag")
		}
		flag, valid := inlineFlag(token.value)
		if !valid {
			return nil, parser.fail(token.position, "unknown flag")
		}
		parser.index++
		if flag == flagLocale {
			return nil, parser.fail(token.position,
				"locale-dependent patterns are not implemented by the Go experiment")
		}
		if flag == flagUnicode && parser.domain == bytesDomain {
			return nil, parser.fail(token.position,
				"bad inline flags: cannot use 'u' flag with a bytes pattern")
		}
		if negative {
			if flag&(flagASCII|flagUnicode|flagLocale) != 0 {
				return nil, parser.fail(token.position,
					"bad inline flags: cannot turn off flags 'a', 'u' and 'L'")
			}
			disable |= flag
		} else {
			if flag&(flagASCII|flagUnicode|flagLocale) != 0 &&
				enable&(flagASCII|flagUnicode|flagLocale) != 0 {
				return nil, parser.fail(token.position,
					"bad inline flags: flags 'a', 'u' and 'L' are incompatible")
			}
			enable |= flag
		}
	}
	if enable&disable != 0 {
		return nil, parser.fail(parser.current().position,
			"bad inline flags: flag turned on and off")
	}
	if negative && disable == 0 {
		return nil, parser.fail(parser.current().position, "missing flag")
	}
	active := (current | enable) &^ disable
	if enable&flagASCII != 0 {
		active &^= flagUnicode
	}
	if enable&flagUnicode != 0 {
		active &^= flagASCII
	}
	if parser.takePlain(')') {
		if negative {
			return nil, parser.fail(position, "missing :")
		}
		return &expression{kind: inlineFlagExpression, flags: active}, nil
	}
	parser.index++ // the independently recognized scoped ':'
	return parser.childGroup(active, position)
}

func (parser *independentParser) conditionalGroup(
	position int, flags uint32,
) (*expression, error) {
	start := parser.current().position
	values := make([]rune, 0)
	for parser.current().kind != endToken && !parser.plain(')') {
		token := parser.current()
		if token.kind != plainToken {
			return nil, parser.fail(start, "bad character in group name")
		}
		values = append(values, token.value)
		parser.index++
	}
	if len(values) == 0 || !parser.takePlain(')') {
		return nil, parser.fail(start, "missing group name")
	}
	var group int
	if number, valid := decimalRunes(values); valid {
		if number == 0 || number > uint64(parser.groups) {
			return nil, parser.fail(start,
				fmt.Sprintf("invalid group reference %s", string(values)))
		}
		group = int(number)
	} else {
		var found bool
		group, found = parser.nameIndex[string(values)]
		if !found {
			return nil, parser.fail(start,
				fmt.Sprintf("unknown group name %q", string(values)))
		}
	}
	parser.depth++
	active := flags
	yes, err := parser.sequence(&active)
	if err != nil {
		parser.depth--
		return nil, err
	}
	no := &expression{kind: emptyExpression, flags: flags}
	if parser.takePlain('|') {
		no, err = parser.sequence(&active)
		if err != nil {
			parser.depth--
			return nil, err
		}
	}
	parser.depth--
	if parser.plain('|') {
		return nil, parser.fail(parser.current().position,
			"conditional backref with more than two branches")
	}
	if !parser.takePlain(')') {
		return nil, parser.fail(position, "missing ), unterminated subpattern")
	}
	return &expression{
		kind: conditionalExpression, flags: flags,
		group: group, children: []*expression{yes, no},
	}, nil
}

func (parser *independentParser) group(position int, flags uint32) (*expression, error) {
	if !parser.takePlain('?') {
		parser.groups++
		number := parser.groups
		parser.groupNames = append(parser.groupNames, "")
		parser.openGroups[number] = true
		child, err := parser.childGroup(flags, position)
		delete(parser.openGroups, number)
		if err != nil {
			return nil, err
		}
		return &expression{
			kind: captureExpression, flags: flags,
			group: number, children: []*expression{child},
		}, nil
	}
	if parser.takePlain(':') {
		return parser.childGroup(flags, position)
	}
	if parser.takePlain('=') || parser.takePlain('!') {
		positive := parser.tokens[parser.index-1].value == '='
		child, err := parser.childGroup(flags, position)
		if err != nil {
			return nil, err
		}
		return &expression{
			kind: lookaheadExpression, flags: flags,
			negative: !positive, children: []*expression{child},
		}, nil
	}
	if parser.takePlain('>') {
		child, err := parser.childGroup(flags, position)
		if err != nil {
			return nil, err
		}
		return &expression{
			kind: atomicExpression, flags: flags,
			children: []*expression{child},
		}, nil
	}
	if parser.takePlain('<') {
		if !parser.takePlain('=') && !parser.takePlain('!') {
			return nil, parser.fail(position+1, "unknown extension ?<")
		}
		positive := parser.tokens[parser.index-1].value == '='
		child, err := parser.childGroup(flags, position)
		if err != nil {
			return nil, err
		}
		minimum, maximum, known := expressionWidth(child)
		if !known || minimum != maximum {
			return nil, parser.fail(-1, "look-behind requires fixed-width pattern")
		}
		return &expression{
			kind: lookbehindExpression, flags: flags,
			negative: !positive, width: minimum,
			children: []*expression{child},
		}, nil
	}
	if parser.takePlain('P') {
		if parser.takePlain('<') {
			name, start, err := parser.readGroupName('>')
			if err != nil {
				return nil, err
			}
			if previous, exists := parser.nameIndex[name]; exists {
				return nil, parser.fail(start, fmt.Sprintf(
					"redefinition of group name %q as group %d; was group %d",
					name, parser.groups+1, previous))
			}
			parser.groups++
			number := parser.groups
			parser.groupNames = append(parser.groupNames, name)
			parser.nameIndex[name] = number
			parser.openGroups[number] = true
			child, childError := parser.childGroup(flags, position)
			delete(parser.openGroups, number)
			if childError != nil {
				return nil, childError
			}
			return &expression{
				kind: captureExpression, flags: flags,
				group: number, children: []*expression{child},
			}, nil
		}
		if parser.takePlain('=') {
			name, start, err := parser.readGroupName(')')
			if err != nil {
				return nil, err
			}
			number, exists := parser.nameIndex[name]
			if !exists {
				return nil, parser.fail(start,
					fmt.Sprintf("unknown group name %q", name))
			}
			if parser.openGroups[number] {
				return nil, parser.fail(start, "cannot refer to an open group")
			}
			return &expression{
				kind: backreferenceExpression, flags: flags, group: number,
			}, nil
		}
		return nil, parser.fail(position+1, "unknown extension ?P")
	}
	if parser.takePlain('(') {
		return parser.conditionalGroup(position, flags)
	}
	if parser.takePlain('#') {
		for parser.current().kind != endToken && !parser.plain(')') {
			parser.index++
		}
		if !parser.takePlain(')') {
			return nil, parser.fail(position, "missing ), unterminated comment")
		}
		return &expression{kind: emptyExpression, flags: flags}, nil
	}
	if token := parser.current(); token.kind == plainToken {
		if _, valid := inlineFlag(token.value); valid || token.value == '-' {
			return parser.flagGroup(position, flags)
		}
	}
	return nil, parser.fail(position+1, "unknown extension")
}

func (parser *independentParser) braceBounds() (int, int, bool, error) {
	if !parser.plain('{') {
		return 0, 0, false, nil
	}
	saved := parser.index
	position := parser.current().position
	parser.index++
	left := make([]rune, 0)
	for token := parser.current(); token.kind == plainToken &&
		token.value >= '0' && token.value <= '9'; token = parser.current() {
		left = append(left, token.value)
		parser.index++
	}
	comma := parser.takePlain(',')
	right := make([]rune, 0)
	if comma {
		for token := parser.current(); token.kind == plainToken &&
			token.value >= '0' && token.value <= '9'; token = parser.current() {
			right = append(right, token.value)
			parser.index++
		}
	}
	if !parser.takePlain('}') || (len(left) == 0 && !comma) ||
		(len(left) == 0 && len(right) == 0) {
		parser.index = saved
		return 0, 0, false, nil
	}
	minimum := uint64(0)
	if len(left) != 0 {
		var valid bool
		minimum, valid = decimalRunes(left)
		if !valid || minimum >= maxRepeat {
			return 0, 0, false,
				parser.fail(position, "the repetition number is too large")
		}
	}
	maximum := minimum
	if comma {
		if len(right) == 0 {
			return int(minimum), -1, true, nil
		}
		var valid bool
		maximum, valid = decimalRunes(right)
		if !valid || maximum >= maxRepeat {
			return 0, 0, false,
				parser.fail(position, "the repetition number is too large")
		}
	}
	if minimum > maximum {
		return 0, 0, false,
			parser.fail(position+1, "min repeat greater than max repeat")
	}
	return int(minimum), int(maximum), true, nil
}

func (parser *independentParser) quantify(
	node *expression, flags uint32,
) (*expression, error) {
	position := parser.current().position
	minimum, maximum := 0, 0
	quantifier := true
	switch {
	case parser.takePlain('*'):
		minimum, maximum = 0, -1
	case parser.takePlain('+'):
		minimum, maximum = 1, -1
	case parser.takePlain('?'):
		minimum, maximum = 0, 1
	default:
		var err error
		minimum, maximum, quantifier, err = parser.braceBounds()
		if err != nil {
			return nil, err
		}
	}
	if !quantifier {
		return node, nil
	}
	if node.kind == anchorExpression || node.kind == boundaryExpression ||
		node.kind == inlineFlagExpression {
		return nil, parser.fail(position, "nothing to repeat")
	}
	repeated := &expression{
		kind: repetitionExpression, flags: flags,
		minimum: minimum, maximum: maximum,
		children: []*expression{node},
	}
	if parser.takePlain('?') {
		repeated.lazy = true
	} else if parser.takePlain('+') {
		repeated.possessive = true
	}
	if parser.plain('*') || parser.plain('+') || parser.plain('?') {
		return nil, parser.fail(parser.current().position, "multiple repeat")
	}
	return repeated, nil
}

func expressionWidth(node *expression) (int, int, bool) {
	switch node.kind {
	case emptyExpression, anchorExpression, boundaryExpression,
		lookaheadExpression, lookbehindExpression, inlineFlagExpression:
		return 0, 0, true
	case literalExpression, classExpression, dotExpression, categoryExpression:
		return 1, 1, true
	case captureExpression, atomicExpression:
		return expressionWidth(node.children[0])
	case backreferenceExpression:
		return 0, 0, false
	case sequenceExpression:
		minimum, maximum := 0, 0
		for _, child := range node.children {
			low, high, known := expressionWidth(child)
			if !known || low > int(^uint(0)>>1)-minimum ||
				high > int(^uint(0)>>1)-maximum {
				return 0, 0, false
			}
			minimum += low
			maximum += high
		}
		return minimum, maximum, true
	case alternativeExpression, conditionalExpression:
		if len(node.children) == 0 {
			return 0, 0, true
		}
		minimum, maximum, known := expressionWidth(node.children[0])
		if !known {
			return 0, 0, false
		}
		for _, child := range node.children[1:] {
			low, high, valid := expressionWidth(child)
			if !valid {
				return 0, 0, false
			}
			if low < minimum {
				minimum = low
			}
			if high > maximum {
				maximum = high
			}
		}
		return minimum, maximum, true
	case repetitionExpression:
		low, high, known := expressionWidth(node.children[0])
		if !known || node.maximum < 0 ||
			(low != 0 && node.minimum > int(^uint(0)>>1)/low) ||
			(high != 0 && node.maximum > int(^uint(0)>>1)/high) {
			return 0, 0, false
		}
		return low * node.minimum, high * node.maximum, true
	default:
		return 0, 0, false
	}
}

type compiledExpression struct {
	domain     inputDomain
	flags      uint32
	root       *expression
	groupCount int
	groupNames []string
}

func compileExpression(
	pattern []rune, domain inputDomain, flags uint32,
) (*compiledExpression, error) {
	if flags&^knownFlags != 0 {
		return nil, issueAt(pattern, -1, "unrecognized regular-expression flags")
	}
	if flags&flagLocale != 0 {
		return nil, issueAt(pattern, -1,
			"locale-dependent patterns are not implemented by the Go experiment")
	}
	if flags&flagDebug != 0 {
		return nil, issueAt(pattern, -1,
			"debug opcode output is not implemented by the Go experiment")
	}
	if domain == bytesDomain && flags&flagUnicode != 0 {
		return nil, issueAt(pattern, -1,
			"cannot use UNICODE flag with a bytes pattern")
	}
	if flags&flagASCII != 0 && flags&flagUnicode != 0 {
		return nil, issueAt(pattern, -1,
			"ASCII and UNICODE flags are incompatible")
	}
	if domain == textDomain && flags&flagASCII == 0 {
		flags |= flagUnicode
	}
	tokens, err := lexPattern(pattern, domain)
	if err != nil {
		return nil, err
	}
	parser := &independentParser{
		pattern: pattern, tokens: tokens, domain: domain,
		nameIndex:  make(map[string]int),
		openGroups: make(map[int]bool), rootFlags: flags,
	}
	root, err := parser.parse(flags)
	if err != nil {
		return nil, err
	}
	return &compiledExpression{
		domain: domain, flags: parser.rootFlags, root: root,
		groupCount: parser.groups,
		groupNames: append([]string(nil), parser.groupNames...),
	}, nil
}

type captureSpan struct {
	start int
	end   int
}

type traversalState struct {
	position int
	spans    []captureSpan
	last     int
}

type matchContinuation func(traversalState) (bool, error)

type independentExecutor struct {
	compiled *compiledExpression
	subject  []rune
	end      int
}

func asciiMode(flags uint32, domain inputDomain) bool {
	return domain == bytesDomain || flags&flagASCII != 0
}

func equalCharacter(left, right rune, flags uint32, domain inputDomain) bool {
	if left == right {
		return true
	}
	if flags&flagIgnoreCase == 0 {
		return false
	}
	if asciiMode(flags, domain) {
		if left >= 'A' && left <= 'Z' {
			left += 'a' - 'A'
		}
		if right >= 'A' && right <= 'Z' {
			right += 'a' - 'A'
		}
		return left == right
	}
	if strings.ContainsRune("Iiİı", left) &&
		strings.ContainsRune("Iiİı", right) {
		return true
	}
	for folded := unicode.SimpleFold(left); folded != left; folded = unicode.SimpleFold(folded) {
		if folded == right {
			return true
		}
	}
	return false
}

func categoryContains(value rune, category rune, flags uint32, domain inputDomain) bool {
	ascii := asciiMode(flags, domain)
	var included bool
	switch unicode.ToLower(category) {
	case 'd':
		if ascii {
			included = value >= '0' && value <= '9'
		} else {
			included = unicode.IsDigit(value)
		}
	case 's':
		if ascii {
			included = strings.ContainsRune(" \t\n\r\v\f", value)
		} else {
			included = unicode.IsSpace(value) ||
				(value >= '\x1c' && value <= '\x1f')
		}
	case 'w':
		if ascii {
			included = value == '_' ||
				(value >= 'a' && value <= 'z') ||
				(value >= 'A' && value <= 'Z') ||
				(value >= '0' && value <= '9')
		} else {
			included = value == '_' || unicode.IsLetter(value) ||
				unicode.IsNumber(value)
		}
	}
	if unicode.IsUpper(category) {
		return !included
	}
	return included
}

func classContains(
	node *expression, value rune, domain inputDomain,
) bool {
	included := false
	for _, term := range node.terms {
		if term.category != 0 {
			if categoryContains(value, term.category, node.flags, domain) {
				included = true
				break
			}
			continue
		}
		if value >= term.low && value <= term.high {
			included = true
			break
		}
		if node.flags&flagIgnoreCase != 0 {
			for candidate := term.low; candidate <= term.high; candidate++ {
				if equalCharacter(candidate, value, node.flags, domain) {
					included = true
					break
				}
				if candidate == unicode.MaxRune {
					break
				}
			}
			if included {
				break
			}
		}
	}
	return included != node.negative
}

func cloneSpans(spans []captureSpan) []captureSpan {
	return append([]captureSpan(nil), spans...)
}

func clearNestedCaptures(node *expression, spans []captureSpan) {
	if node.kind == captureExpression && node.group < len(spans) {
		spans[node.group] = captureSpan{start: -1, end: -1}
	}
	for _, child := range node.children {
		clearNestedCaptures(child, spans)
	}
}

func (executor *independentExecutor) visit(
	node *expression, state traversalState, next matchContinuation,
) (bool, error) {
	domain := executor.compiled.domain
	switch node.kind {
	case emptyExpression:
		return next(state)
	case literalExpression:
		if state.position < executor.end &&
			equalCharacter(node.value, executor.subject[state.position], node.flags, domain) {
			state.position++
			return next(state)
		}
		return false, nil
	case dotExpression:
		if state.position < executor.end &&
			(node.flags&flagDotAll != 0 || executor.subject[state.position] != '\n') {
			state.position++
			return next(state)
		}
		return false, nil
	case classExpression:
		if state.position < executor.end &&
			classContains(node, executor.subject[state.position], domain) {
			state.position++
			return next(state)
		}
		return false, nil
	case categoryExpression:
		if state.position < executor.end && categoryContains(
			executor.subject[state.position], node.value, node.flags, domain,
		) {
			state.position++
			return next(state)
		}
		return false, nil
	case anchorExpression:
		valid := false
		switch node.value {
		case '^':
			valid = state.position == 0 ||
				(node.flags&flagMultiline != 0 && state.position > 0 &&
					executor.subject[state.position-1] == '\n')
		case '$':
			valid = state.position == executor.end ||
				(state.position+1 == executor.end &&
					executor.subject[state.position] == '\n') ||
				(node.flags&flagMultiline != 0 &&
					state.position < executor.end &&
					executor.subject[state.position] == '\n')
		case 'A':
			valid = state.position == 0
		case 'Z', 'z':
			valid = state.position == executor.end
		}
		if valid {
			return next(state)
		}
		return false, nil
	case boundaryExpression:
		left := state.position > 0 && categoryContains(
			executor.subject[state.position-1], 'w', node.flags, domain,
		)
		right := state.position < executor.end && categoryContains(
			executor.subject[state.position], 'w', node.flags, domain,
		)
		if (left != right) != node.negative {
			return next(state)
		}
		return false, nil
	case sequenceExpression:
		var walk func(int, traversalState) (bool, error)
		walk = func(index int, current traversalState) (bool, error) {
			if index == len(node.children) {
				return next(current)
			}
			return executor.visit(node.children[index], current,
				func(updated traversalState) (bool, error) {
					return walk(index+1, updated)
				})
		}
		return walk(0, state)
	case alternativeExpression:
		for _, child := range node.children {
			stop, err := executor.visit(child, state, next)
			if err != nil || stop {
				return stop, err
			}
		}
		return false, nil
	case captureExpression:
		start := state.position
		return executor.visit(node.children[0], state,
			func(updated traversalState) (bool, error) {
				updated.spans = cloneSpans(updated.spans)
				updated.spans[node.group] = captureSpan{
					start: start, end: updated.position,
				}
				updated.last = node.group
				return next(updated)
			})
	case backreferenceExpression:
		span := state.spans[node.group]
		if span.start < 0 || span.end < span.start {
			return false, nil
		}
		width := span.end - span.start
		if width > executor.end-state.position {
			return false, nil
		}
		for offset := 0; offset < width; offset++ {
			if !equalCharacter(
				executor.subject[span.start+offset],
				executor.subject[state.position+offset],
				node.flags, domain,
			) {
				return false, nil
			}
		}
		state.position += width
		return next(state)
	case repetitionExpression:
		return executor.repeat(node, state, 0, next)
	case lookaheadExpression:
		var found *traversalState
		_, err := executor.visit(node.children[0], state,
			func(updated traversalState) (bool, error) {
				copy := updated
				found = &copy
				return true, nil
			})
		if err != nil {
			return false, err
		}
		if node.negative {
			if found == nil {
				return next(state)
			}
			return false, nil
		}
		if found != nil {
			found.position = state.position
			return next(*found)
		}
		return false, nil
	case lookbehindExpression:
		if state.position < node.width {
			if node.negative {
				return next(state)
			}
			return false, nil
		}
		origin := state.position
		behind := state
		behind.position -= node.width
		var found *traversalState
		_, err := executor.visit(node.children[0], behind,
			func(updated traversalState) (bool, error) {
				if updated.position != origin {
					return false, nil
				}
				copy := updated
				found = &copy
				return true, nil
			})
		if err != nil {
			return false, err
		}
		if node.negative {
			if found == nil {
				return next(state)
			}
			return false, nil
		}
		if found != nil {
			found.position = origin
			return next(*found)
		}
		return false, nil
	case atomicExpression:
		var found *traversalState
		_, err := executor.visit(node.children[0], state,
			func(updated traversalState) (bool, error) {
				copy := updated
				found = &copy
				return true, nil
			})
		if err != nil {
			return false, err
		}
		if found != nil {
			return next(*found)
		}
		return false, nil
	case conditionalExpression:
		branch := 1
		if state.spans[node.group].start >= 0 {
			branch = 0
		}
		return executor.visit(node.children[branch], state, next)
	default:
		return false, fmt.Errorf("unrecognized owned Go expression kind %d", node.kind)
	}
}

func (executor *independentExecutor) repeat(
	node *expression, state traversalState, count int, next matchContinuation,
) (bool, error) {
	if node.possessive {
		current := state
		consumed := count
		for node.maximum < 0 || consumed < node.maximum {
			seed := current
			seed.spans = cloneSpans(current.spans)
			clearNestedCaptures(node.children[0], seed.spans)
			var first *traversalState
			_, err := executor.visit(node.children[0], seed,
				func(updated traversalState) (bool, error) {
					copy := updated
					first = &copy
					return true, nil
				})
			if err != nil {
				return false, err
			}
			if first == nil {
				break
			}
			consumed++
			unchanged := first.position == current.position
			current = *first
			if unchanged && consumed >= node.minimum {
				break
			}
		}
		if consumed >= node.minimum {
			return next(current)
		}
		return false, nil
	}
	if node.lazy && count >= node.minimum {
		stop, err := next(state)
		if err != nil || stop {
			return stop, err
		}
	}
	if node.maximum < 0 || count < node.maximum {
		seed := state
		seed.spans = cloneSpans(state.spans)
		clearNestedCaptures(node.children[0], seed.spans)
		stop, err := executor.visit(node.children[0], seed,
			func(updated traversalState) (bool, error) {
				if updated.position == state.position {
					if count+1 < node.minimum {
						return executor.repeat(node, updated, count+1, next)
					}
					return next(updated)
				}
				return executor.repeat(node, updated, count+1, next)
			})
		if err != nil || stop {
			return stop, err
		}
	}
	if !node.lazy && count >= node.minimum {
		return next(state)
	}
	return false, nil
}

func (compiled *compiledExpression) firstMatch(
	subject []rune, start, end int, searching, full, rejectEmpty bool,
) (*traversalState, error) {
	if start < 0 {
		start = 0
	}
	if start > len(subject) {
		start = len(subject)
	}
	if end < 0 {
		end = 0
	}
	if end > len(subject) {
		end = len(subject)
	}
	if start > end {
		return nil, nil
	}
	executor := &independentExecutor{
		compiled: compiled, subject: subject, end: end,
	}
	for position := start; position <= end; position++ {
		spans := make([]captureSpan, compiled.groupCount+1)
		for index := range spans {
			spans[index] = captureSpan{start: -1, end: -1}
		}
		initial := traversalState{
			position: position, spans: spans, last: -1,
		}
		var selected *traversalState
		_, err := executor.visit(compiled.root, initial,
			func(updated traversalState) (bool, error) {
				if full && updated.position != end {
					return false, nil
				}
				if rejectEmpty && position == start &&
					updated.position == position {
					return false, nil
				}
				updated.spans = cloneSpans(updated.spans)
				updated.spans[0] = captureSpan{
					start: position, end: updated.position,
				}
				copy := updated
				selected = &copy
				return true, nil
			})
		if err != nil {
			return nil, err
		}
		if selected != nil {
			return selected, nil
		}
		if !searching {
			break
		}
	}
	return nil, nil
}
