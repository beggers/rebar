// Package main owns an independent Python-compatible regular-expression engine.
//
// The parser, instruction compiler, ordered backtracker, and cgo handles in
// this file are specific to the Go candidate. No external matching implementation, Python
// matching engine, or other rebar candidate participates in matching.
package main

/*
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
*/
import "C"

import (
	"fmt"
	"runtime/cgo"
	"strconv"
	"unicode"
	"unsafe"
)

const (
	flagTemplate   uint32 = 1
	flagIgnoreCase uint32 = 2
	flagLocale     uint32 = 4
	flagMultiline  uint32 = 8
	flagDotAll     uint32 = 16
	flagUnicode    uint32 = 32
	flagVerbose    uint32 = 64
	flagDebug      uint32 = 128
	flagASCII      uint32 = 256

	traitASCIIDigit   uint8 = 1 << 0
	traitASCIISpace   uint8 = 1 << 1
	traitASCIIWord    uint8 = 1 << 2
	traitUnicodeDigit uint8 = 1 << 3
	traitUnicodeSpace uint8 = 1 << 4
	traitUnicodeWord  uint8 = 1 << 5
	traitLocaleWord   uint8 = 1 << 6

	compileInvalid = 1
	compileName    = 2
	compileLimit   = 3

	unlimitedRepeat = -1
	maxRepeat       = uint64(4294967295)
	maxParseDepth   = 1000
)

type failure struct {
	message  string
	position int
	kind     int
}

func (e *failure) Error() string {
	return e.message
}

type category uint8

const (
	categoryDigit category = iota + 1
	categoryNotDigit
	categorySpace
	categoryNotSpace
	categoryWord
	categoryNotWord
)

type nodeKind uint8

const (
	nodeEmpty nodeKind = iota
	nodeLiteral
	nodeAny
	nodeCategory
	nodeClass
	nodeSequence
	nodeAlternation
	nodeGroup
	nodeRepeat
	nodeBackreference
	nodeAnchor
	nodeLook
	nodeConditional
	nodeAtomic
)

type anchor uint8

const (
	anchorBeginning anchor = iota + 1
	anchorEnd
	anchorAbsoluteBeginning
	anchorAbsoluteEnd
	anchorWordBoundary
	anchorNotWordBoundary
)

type classItem struct {
	first    rune
	last     rune
	category category
}

type characterClass struct {
	negated bool
	items   []classItem
}

type expression struct {
	kind       nodeKind
	children   []*expression
	character  rune
	category   category
	class      *characterClass
	flags      uint32
	group      int
	minimum    int
	maximum    int
	lazy       bool
	positive   bool
	lookbehind bool
	anchor     anchor
}

type namedGroup struct {
	name   string
	number int
}

type parser struct {
	source      []rune
	offset      int
	flags       uint32
	byteMode    bool
	groupCount  int
	groupByName map[string]int
	namedGroups []namedGroup
	namedRunes  map[int]rune
	openGroups  []int
	depth       int
}

func (p *parser) invalid(message string, position int) *failure {
	if position < 0 {
		position = 0
	}
	return &failure{message: message, position: position, kind: compileInvalid}
}

func (p *parser) skipVerbose() *failure {
	if p.flags&flagVerbose == 0 {
		return nil
	}
	for p.offset < len(p.source) {
		current := p.source[p.offset]
		switch current {
		case ' ', '\t', '\n', '\r', '\v', '\f':
			p.offset++
		case '#':
			p.offset++
			for p.offset < len(p.source) {
				if p.source[p.offset] == '\\' {
					if p.offset+1 == len(p.source) {
						return p.invalid("bad escape (end of pattern)", p.offset)
					}
					p.offset += 2
					continue
				}
				if p.source[p.offset] == '\n' {
					p.offset++
					break
				}
				p.offset++
			}
		default:
			return nil
		}
	}
	return nil
}

func (p *parser) parse() (*expression, *failure) {
	result, err := p.alternation()
	if err != nil {
		return nil, err
	}
	if err = p.skipVerbose(); err != nil {
		return nil, err
	}
	if p.offset != len(p.source) {
		if p.source[p.offset] == ')' {
			return nil, p.invalid("unbalanced parenthesis", p.offset)
		}
		return nil, p.invalid("unexpected end of pattern", p.offset)
	}
	return result, nil
}

func (p *parser) alternation() (*expression, *failure) {
	p.depth++
	if p.depth > maxParseDepth {
		p.depth--
		return nil, &failure{
			message:  "maximum recursion depth exceeded",
			position: p.offset,
			kind:     compileLimit,
		}
	}
	defer func() { p.depth-- }()

	branches := make([]*expression, 0, 2)
	for {
		branch, err := p.sequence()
		if err != nil {
			return nil, err
		}
		branches = append(branches, branch)
		if err = p.skipVerbose(); err != nil {
			return nil, err
		}
		if p.offset >= len(p.source) || p.source[p.offset] != '|' {
			break
		}
		p.offset++
	}
	if len(branches) == 1 {
		return branches[0], nil
	}
	return &expression{kind: nodeAlternation, children: branches}, nil
}

func (p *parser) sequence() (*expression, *failure) {
	children := make([]*expression, 0, 4)
	for {
		if err := p.skipVerbose(); err != nil {
			return nil, err
		}
		if p.offset >= len(p.source) {
			break
		}
		current := p.source[p.offset]
		if current == ')' || current == '|' {
			break
		}
		if current == '*' || current == '+' || current == '?' {
			return nil, p.invalid("nothing to repeat", p.offset)
		}
		atom, err := p.atom()
		if err != nil {
			return nil, err
		}
		if atom == nil {
			continue
		}
		atom, err = p.quantifier(atom)
		if err != nil {
			return nil, err
		}
		children = append(children, atom)
	}
	switch len(children) {
	case 0:
		return &expression{kind: nodeEmpty}, nil
	case 1:
		return children[0], nil
	default:
		return &expression{kind: nodeSequence, children: children}, nil
	}
}

func (p *parser) atom() (*expression, *failure) {
	position := p.offset
	current := p.source[position]
	p.offset++
	switch current {
	case '.':
		return &expression{kind: nodeAny, flags: p.flags}, nil
	case '^':
		return &expression{kind: nodeAnchor, anchor: anchorBeginning, flags: p.flags}, nil
	case '$':
		return &expression{kind: nodeAnchor, anchor: anchorEnd, flags: p.flags}, nil
	case '[':
		return p.characterSet(position)
	case '(':
		return p.group(position)
	case '\\':
		return p.escape(position, false)
	case '{':
		return &expression{kind: nodeLiteral, character: current, flags: p.flags}, nil
	default:
		return &expression{kind: nodeLiteral, character: current, flags: p.flags}, nil
	}
}

func hexDigit(value rune) (uint32, bool) {
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

func (p *parser) hexadecimal(position int, count int, prefix string) (*expression, *failure) {
	if p.offset+count > len(p.source) {
		return nil, p.invalid("incomplete escape "+prefix, position)
	}
	var result uint32
	for index := 0; index < count; index++ {
		digit, ok := hexDigit(p.source[p.offset+index])
		if !ok {
			return nil, p.invalid("incomplete escape "+prefix, position)
		}
		result = result<<4 | digit
	}
	p.offset += count
	if result > unicode.MaxRune {
		return nil, p.invalid("bad escape "+prefix, position)
	}
	return &expression{kind: nodeLiteral, character: rune(result), flags: p.flags}, nil
}

func (p *parser) namedCharacter(position int) (*expression, *failure) {
	if p.byteMode {
		return nil, p.invalid("bad escape \\N", position)
	}
	if p.offset >= len(p.source) || p.source[p.offset] != '{' {
		return nil, p.invalid("missing {", p.offset)
	}
	p.offset++
	begin := p.offset
	for p.offset < len(p.source) && p.source[p.offset] != '}' {
		p.offset++
	}
	if p.offset >= len(p.source) {
		return nil, p.invalid("missing }, unterminated name", begin)
	}
	name := string(p.source[begin:p.offset])
	p.offset++
	if name == "" {
		return nil, p.invalid("missing character name", begin)
	}
	if value, ok := p.namedRunes[position]; ok {
		return &expression{kind: nodeLiteral, character: value, flags: p.flags}, nil
	}
	return nil, &failure{message: name, position: position, kind: compileName}
}

func (p *parser) numericEscape(position int, first rune, inClass bool) (*expression, *failure) {
	if first == '0' {
		value := uint32(0)
		for count := 0; count < 2 && p.offset < len(p.source); count++ {
			digit := p.source[p.offset]
			if digit < '0' || digit > '7' {
				break
			}
			value = value*8 + uint32(digit-'0')
			p.offset++
		}
		return &expression{kind: nodeLiteral, character: rune(value), flags: p.flags}, nil
	}
	if first <= '7' && p.offset+1 < len(p.source) &&
		p.source[p.offset] >= '0' && p.source[p.offset] <= '7' &&
		p.source[p.offset+1] >= '0' && p.source[p.offset+1] <= '7' {
		value := uint32(first-'0')*64 +
			uint32(p.source[p.offset]-'0')*8 +
			uint32(p.source[p.offset+1]-'0')
		if value > 255 {
			spelling := string([]rune{first, p.source[p.offset], p.source[p.offset+1]})
			return nil, p.invalid(
				"octal escape value \\"+spelling+" outside of range 0-0o377",
				position,
			)
		}
		p.offset += 2
		return &expression{kind: nodeLiteral, character: rune(value), flags: p.flags}, nil
	}
	if inClass {
		return nil, p.invalid("bad escape \\"+string(first), position)
	}
	number := int(first - '0')
	if p.offset < len(p.source) && p.source[p.offset] >= '0' && p.source[p.offset] <= '9' {
		number = number*10 + int(p.source[p.offset]-'0')
		p.offset++
	}
	if number < 1 || number > p.groupCount {
		return nil, p.invalid(fmt.Sprintf("invalid group reference %d", number), position+1)
	}
	for _, open := range p.openGroups {
		if open == number {
			return nil, p.invalid("cannot refer to an open group", position)
		}
	}
	return &expression{kind: nodeBackreference, group: number, flags: p.flags}, nil
}

func (p *parser) escape(position int, inClass bool) (*expression, *failure) {
	if p.offset >= len(p.source) {
		return nil, p.invalid("bad escape (end of pattern)", position)
	}
	current := p.source[p.offset]
	p.offset++
	simple := map[rune]rune{
		'a': '\a',
		'b': '\b',
		'f': '\f',
		'n': '\n',
		'r': '\r',
		't': '\t',
		'v': '\v',
	}
	if current == 'b' && !inClass {
		return &expression{kind: nodeAnchor, anchor: anchorWordBoundary, flags: p.flags}, nil
	}
	if value, ok := simple[current]; ok {
		return &expression{kind: nodeLiteral, character: value, flags: p.flags}, nil
	}
	categories := map[rune]category{
		'd': categoryDigit,
		'D': categoryNotDigit,
		's': categorySpace,
		'S': categoryNotSpace,
		'w': categoryWord,
		'W': categoryNotWord,
	}
	if value, ok := categories[current]; ok {
		return &expression{kind: nodeCategory, category: value, flags: p.flags}, nil
	}
	switch current {
	case 'B':
		if inClass {
			return nil, p.invalid("bad escape \\B", position)
		}
		return &expression{kind: nodeAnchor, anchor: anchorNotWordBoundary, flags: p.flags}, nil
	case 'A':
		if inClass {
			return nil, p.invalid("bad escape \\A", position)
		}
		return &expression{kind: nodeAnchor, anchor: anchorAbsoluteBeginning, flags: p.flags}, nil
	case 'Z', 'z':
		if inClass {
			return nil, p.invalid("bad escape \\"+string(current), position)
		}
		return &expression{kind: nodeAnchor, anchor: anchorAbsoluteEnd, flags: p.flags}, nil
	case 'x':
		return p.hexadecimal(position, 2, "\\x")
	case 'u':
		if p.byteMode {
			return nil, p.invalid("bad escape \\u", position)
		}
		return p.hexadecimal(position, 4, "\\u")
	case 'U':
		if p.byteMode {
			return nil, p.invalid("bad escape \\U", position)
		}
		return p.hexadecimal(position, 8, "\\U")
	case 'N':
		return p.namedCharacter(position)
	}
	if current >= '0' && current <= '9' {
		return p.numericEscape(position, current, inClass)
	}
	if (current >= 'A' && current <= 'Z') || (current >= 'a' && current <= 'z') {
		return nil, p.invalid("bad escape \\"+string(current), position)
	}
	return &expression{kind: nodeLiteral, character: current, flags: p.flags}, nil
}

func (p *parser) setItem(opening int) (classItem, *failure) {
	if p.offset >= len(p.source) {
		return classItem{}, p.invalid("unterminated character set", opening)
	}
	position := p.offset
	current := p.source[p.offset]
	p.offset++
	if current != '\\' {
		return classItem{first: current, last: current}, nil
	}
	value, err := p.escape(position, true)
	if err != nil {
		return classItem{}, err
	}
	if value.kind == nodeCategory {
		return classItem{category: value.category}, nil
	}
	return classItem{first: value.character, last: value.character}, nil
}

func (p *parser) characterSet(opening int) (*expression, *failure) {
	result := &characterClass{}
	if p.offset < len(p.source) && p.source[p.offset] == '^' {
		result.negated = true
		p.offset++
	}
	first := true
	for p.offset < len(p.source) {
		if p.source[p.offset] == ']' && !first {
			p.offset++
			return &expression{kind: nodeClass, class: result, flags: p.flags}, nil
		}
		first = false
		leftPosition := p.offset
		left, err := p.setItem(opening)
		if err != nil {
			return nil, err
		}
		if p.offset < len(p.source) && p.source[p.offset] == '-' &&
			p.offset+1 < len(p.source) && p.source[p.offset+1] != ']' {
			p.offset++
			right, rightErr := p.setItem(opening)
			if rightErr != nil {
				return nil, rightErr
			}
			if left.category != 0 || right.category != 0 || left.first > right.first {
				leftText := string(left.first)
				rightText := string(right.first)
				if left.category != 0 {
					leftText = "\\d"
				}
				if right.category != 0 {
					rightText = "\\d"
				}
				return nil, p.invalid(
					"bad character range "+leftText+"-"+rightText,
					leftPosition,
				)
			}
			left.last = right.first
		}
		result.items = append(result.items, left)
	}
	return nil, p.invalid("unterminated character set", opening)
}

func validGroupName(source []rune, byteMode bool) bool {
	if len(source) == 0 {
		return false
	}
	for index, value := range source {
		if byteMode && value > unicode.MaxASCII {
			return false
		}
		if value == '_' {
			continue
		}
		if index == 0 {
			if !unicode.IsLetter(value) {
				return false
			}
		} else if !unicode.IsLetter(value) && !unicode.IsDigit(value) &&
			!unicode.Is(unicode.Mn, value) && !unicode.Is(unicode.Mc, value) &&
			!unicode.Is(unicode.Pc, value) {
			return false
		}
	}
	return true
}

func (p *parser) closeGroup(child *expression, opening int) (*expression, *failure) {
	if err := p.skipVerbose(); err != nil {
		return nil, err
	}
	if p.offset >= len(p.source) || p.source[p.offset] != ')' {
		return nil, p.invalid("missing ), unterminated subpattern", opening)
	}
	p.offset++
	return child, nil
}

func flagFor(value rune) uint32 {
	switch value {
	case 'a':
		return flagASCII
	case 'i':
		return flagIgnoreCase
	case 'L':
		return flagLocale
	case 'm':
		return flagMultiline
	case 's':
		return flagDotAll
	case 'u':
		return flagUnicode
	case 'x':
		return flagVerbose
	default:
		return 0
	}
}

func (p *parser) inlineFlags(opening int) (*expression, *failure) {
	added := uint32(0)
	removed := uint32(0)
	negative := false
	for p.offset < len(p.source) {
		value := p.source[p.offset]
		if value == ':' || value == ')' {
			break
		}
		if value == '-' {
			if negative {
				return nil, p.invalid("bad inline flags: missing flag", p.offset)
			}
			negative = true
			p.offset++
			continue
		}
		bit := flagFor(value)
		if bit == 0 {
			return nil, p.invalid("unknown extension ?"+string(value), opening+1)
		}
		if p.byteMode && bit == flagUnicode {
			return nil, p.invalid("bad inline flags: cannot use 'u' flag with a bytes pattern", p.offset)
		}
		if !p.byteMode && bit == flagLocale {
			return nil, p.invalid("bad inline flags: cannot use 'L' flag with a str pattern", p.offset)
		}
		if negative {
			if bit&(flagASCII|flagLocale|flagUnicode) != 0 {
				return nil, p.invalid("bad inline flags: cannot turn off flags 'a', 'u' and 'L'", p.offset)
			}
			removed |= bit
		} else {
			added |= bit
		}
		p.offset++
	}
	if p.offset >= len(p.source) {
		return nil, p.invalid("missing -, : or )", p.offset)
	}
	if added&removed != 0 {
		return nil, p.invalid("bad inline flags: flag turned on and off", p.offset)
	}
	if added&(flagASCII|flagLocale|flagUnicode) != 0 {
		addedModes := added & (flagASCII | flagLocale | flagUnicode)
		if addedModes&(addedModes-1) != 0 {
			return nil, p.invalid("bad inline flags: flags 'a', 'u' and 'L' are incompatible", p.offset)
		}
	}
	if p.source[p.offset] == ')' {
		if negative {
			return nil, p.invalid("missing :", p.offset)
		}
		if opening != 0 {
			return nil, p.invalid("global flags not at the start of the expression", opening)
		}
		p.flags |= added
		p.offset++
		return nil, nil
	}
	p.offset++
	previous := p.flags
	if added&(flagASCII|flagLocale|flagUnicode) != 0 {
		p.flags &^= flagASCII | flagLocale | flagUnicode
	}
	p.flags = (p.flags | added) &^ removed
	child, err := p.alternation()
	p.flags = previous
	if err != nil {
		return nil, err
	}
	return p.closeGroup(child, opening)
}

func (p *parser) readGroupName(delimiter rune, opening int) (string, int, *failure) {
	begin := p.offset
	for p.offset < len(p.source) && p.source[p.offset] != delimiter {
		p.offset++
	}
	if p.offset >= len(p.source) {
		return "", begin, p.invalid("missing "+string(delimiter)+", unterminated name", begin)
	}
	source := p.source[begin:p.offset]
	p.offset++
	if !validGroupName(source, p.byteMode) {
		return "", begin, p.invalid(
			fmt.Sprintf("bad character in group name %q", string(source)),
			begin,
		)
	}
	return string(source), begin, nil
}

func (p *parser) capturingGroup(opening int, name string, namePosition int) (*expression, *failure) {
	p.groupCount++
	number := p.groupCount
	if name != "" {
		if previous, exists := p.groupByName[name]; exists {
			return nil, p.invalid(
				fmt.Sprintf(
					"redefinition of group name %q as group %d; was group %d",
					name,
					number,
					previous,
				),
				namePosition,
			)
		}
		p.groupByName[name] = number
		p.namedGroups = append(p.namedGroups, namedGroup{name: name, number: number})
	}
	p.openGroups = append(p.openGroups, number)
	child, err := p.alternation()
	p.openGroups = p.openGroups[:len(p.openGroups)-1]
	if err != nil {
		return nil, err
	}
	child, err = p.closeGroup(child, opening)
	if err != nil {
		return nil, err
	}
	return &expression{kind: nodeGroup, group: number, children: []*expression{child}}, nil
}

func (p *parser) conditionalGroup(opening int) (*expression, *failure) {
	begin := p.offset
	for p.offset < len(p.source) && p.source[p.offset] != ')' {
		p.offset++
	}
	if p.offset >= len(p.source) {
		return nil, p.invalid("missing ), unterminated name", begin)
	}
	identity := string(p.source[begin:p.offset])
	p.offset++
	number, numberErr := strconv.Atoi(identity)
	if numberErr != nil {
		var ok bool
		number, ok = p.groupByName[identity]
		if !ok {
			return nil, p.invalid(fmt.Sprintf("unknown group name %q", identity), begin)
		}
	}
	if number < 1 || number > p.groupCount {
		return nil, p.invalid(fmt.Sprintf("invalid group reference %d", number), begin)
	}
	yes, err := p.sequence()
	if err != nil {
		return nil, err
	}
	no := &expression{kind: nodeEmpty}
	if p.offset < len(p.source) && p.source[p.offset] == '|' {
		p.offset++
		no, err = p.sequence()
		if err != nil {
			return nil, err
		}
		if p.offset < len(p.source) && p.source[p.offset] == '|' {
			return nil, p.invalid("conditional backref with more than two branches", p.offset)
		}
	}
	result := &expression{
		kind:     nodeConditional,
		group:    number,
		children: []*expression{yes, no},
	}
	return p.closeGroup(result, opening)
}

func (p *parser) group(opening int) (*expression, *failure) {
	if p.offset >= len(p.source) || p.source[p.offset] != '?' {
		return p.capturingGroup(opening, "", 0)
	}
	p.offset++
	if p.offset >= len(p.source) {
		return nil, p.invalid("unexpected end of pattern", p.offset)
	}
	marker := p.source[p.offset]
	p.offset++
	switch marker {
	case ':':
		child, err := p.alternation()
		if err != nil {
			return nil, err
		}
		return p.closeGroup(child, opening)
	case '#':
		for p.offset < len(p.source) {
			switch p.source[p.offset] {
			case '\\':
				if p.offset+1 >= len(p.source) {
					return nil, p.invalid("bad escape (end of pattern)", p.offset)
				}
				p.offset += 2
			case ')':
				p.offset++
				return &expression{kind: nodeEmpty}, nil
			default:
				p.offset++
			}
		}
		return nil, p.invalid("missing ), unterminated comment", opening)
	case '=':
		child, err := p.alternation()
		if err != nil {
			return nil, err
		}
		child, err = p.closeGroup(child, opening)
		if err != nil {
			return nil, err
		}
		return &expression{kind: nodeLook, children: []*expression{child}, positive: true}, nil
	case '!':
		child, err := p.alternation()
		if err != nil {
			return nil, err
		}
		child, err = p.closeGroup(child, opening)
		if err != nil {
			return nil, err
		}
		return &expression{kind: nodeLook, children: []*expression{child}, positive: false}, nil
	case '>':
		child, err := p.alternation()
		if err != nil {
			return nil, err
		}
		child, err = p.closeGroup(child, opening)
		if err != nil {
			return nil, err
		}
		return &expression{kind: nodeAtomic, children: []*expression{child}}, nil
	case '<':
		if p.offset >= len(p.source) ||
			(p.source[p.offset] != '=' && p.source[p.offset] != '!') {
			return nil, p.invalid("unknown extension ?<", opening+1)
		}
		positive := p.source[p.offset] == '='
		p.offset++
		child, err := p.alternation()
		if err != nil {
			return nil, err
		}
		child, err = p.closeGroup(child, opening)
		if err != nil {
			return nil, err
		}
		low, high := expressionWidth(child)
		if low != high || high == unlimitedRepeat {
			return nil, p.invalid("look-behind requires fixed-width pattern", opening)
		}
		return &expression{
			kind:       nodeLook,
			children:   []*expression{child},
			positive:   positive,
			lookbehind: true,
			minimum:    low,
		}, nil
	case 'P':
		if p.offset >= len(p.source) {
			return nil, p.invalid("unexpected end of pattern", p.offset)
		}
		switch p.source[p.offset] {
		case '<':
			p.offset++
			name, position, err := p.readGroupName('>', opening)
			if err != nil {
				return nil, err
			}
			return p.capturingGroup(opening, name, position)
		case '=':
			p.offset++
			name, position, err := p.readGroupName(')', opening)
			if err != nil {
				return nil, err
			}
			number, exists := p.groupByName[name]
			if !exists {
				return nil, p.invalid(fmt.Sprintf("unknown group name %q", name), position)
			}
			for _, open := range p.openGroups {
				if open == number {
					return nil, p.invalid("cannot refer to an open group", opening)
				}
			}
			return &expression{kind: nodeBackreference, group: number, flags: p.flags}, nil
		default:
			return nil, p.invalid("unknown extension ?P"+string(p.source[p.offset]), opening+1)
		}
	case '(':
		return p.conditionalGroup(opening)
	default:
		if marker == '-' || flagFor(marker) != 0 {
			p.offset--
			return p.inlineFlags(opening)
		}
		return nil, p.invalid("unknown extension ?"+string(marker), opening+1)
	}
}

func boundedNumber(values []rune) (int, bool) {
	if len(values) == 0 {
		return 0, false
	}
	for _, value := range values {
		if value < '0' || value > '9' {
			return 0, false
		}
	}
	number, err := strconv.ParseUint(string(values), 10, 64)
	if err != nil || number > maxRepeat {
		return 0, false
	}
	return int(number), true
}

func (p *parser) quantifier(child *expression) (*expression, *failure) {
	if err := p.skipVerbose(); err != nil {
		return nil, err
	}
	if p.offset >= len(p.source) {
		return child, nil
	}
	begin := p.offset
	minimum := 0
	maximum := 0
	switch p.source[p.offset] {
	case '*':
		minimum, maximum = 0, unlimitedRepeat
		p.offset++
	case '+':
		minimum, maximum = 1, unlimitedRepeat
		p.offset++
	case '?':
		minimum, maximum = 0, 1
		p.offset++
	case '{':
		p.offset++
		start := p.offset
		for p.offset < len(p.source) &&
			p.source[p.offset] >= '0' && p.source[p.offset] <= '9' {
			p.offset++
		}
		minimumText := p.source[start:p.offset]
		if p.offset >= len(p.source) ||
			(p.source[p.offset] != ',' && p.source[p.offset] != '}') {
			p.offset = begin
			return child, nil
		}
		if len(minimumText) > 0 {
			var ok bool
			minimum, ok = boundedNumber(minimumText)
			if !ok {
				return nil, &failure{
					message:  "the repetition number is too large",
					position: begin,
					kind:     compileLimit,
				}
			}
		}
		if p.source[p.offset] == '}' {
			if len(minimumText) == 0 {
				p.offset = begin
				return child, nil
			}
			maximum = minimum
			p.offset++
		} else {
			p.offset++
			start = p.offset
			for p.offset < len(p.source) &&
				p.source[p.offset] >= '0' && p.source[p.offset] <= '9' {
				p.offset++
			}
			if p.offset >= len(p.source) || p.source[p.offset] != '}' {
				p.offset = begin
				return child, nil
			}
			maximumText := p.source[start:p.offset]
			if len(maximumText) == 0 {
				maximum = unlimitedRepeat
			} else {
				var ok bool
				maximum, ok = boundedNumber(maximumText)
				if !ok {
					return nil, &failure{
						message:  "the repetition number is too large",
						position: begin,
						kind:     compileLimit,
					}
				}
				if maximum < minimum {
					return nil, p.invalid("min repeat greater than max repeat", begin)
				}
			}
			p.offset++
		}
	default:
		return child, nil
	}
	if child.kind == nodeAnchor || child.kind == nodeLook {
		return nil, p.invalid("nothing to repeat", begin)
	}
	result := &expression{
		kind:     nodeRepeat,
		children: []*expression{child},
		minimum:  minimum,
		maximum:  maximum,
	}
	if p.offset < len(p.source) {
		switch p.source[p.offset] {
		case '?':
			result.lazy = true
			p.offset++
		case '+':
			p.offset++
			result = &expression{kind: nodeAtomic, children: []*expression{result}}
		}
	}
	if p.offset < len(p.source) {
		switch p.source[p.offset] {
		case '*', '+', '?':
			return nil, p.invalid("multiple repeat", p.offset)
		}
	}
	return result, nil
}

func saturatedAdd(first int, second int) int {
	if first == unlimitedRepeat || second == unlimitedRepeat {
		return unlimitedRepeat
	}
	maximum := int(^uint(0) >> 1)
	if first > maximum-second {
		return unlimitedRepeat
	}
	return first + second
}

func saturatedMultiply(first int, second int) int {
	if first == 0 || second == 0 {
		return 0
	}
	if first == unlimitedRepeat || second == unlimitedRepeat {
		return unlimitedRepeat
	}
	maximum := int(^uint(0) >> 1)
	if first > maximum/second {
		return unlimitedRepeat
	}
	return first * second
}

func expressionWidth(value *expression) (int, int) {
	switch value.kind {
	case nodeEmpty, nodeAnchor, nodeLook:
		return 0, 0
	case nodeLiteral, nodeAny, nodeCategory, nodeClass:
		return 1, 1
	case nodeBackreference:
		return 0, unlimitedRepeat
	case nodeGroup, nodeAtomic:
		return expressionWidth(value.children[0])
	case nodeSequence:
		minimum, maximum := 0, 0
		for _, child := range value.children {
			low, high := expressionWidth(child)
			minimum = saturatedAdd(minimum, low)
			maximum = saturatedAdd(maximum, high)
		}
		return minimum, maximum
	case nodeAlternation, nodeConditional:
		minimum := int(^uint(0) >> 1)
		maximum := 0
		for _, child := range value.children {
			low, high := expressionWidth(child)
			if low < minimum {
				minimum = low
			}
			if high == unlimitedRepeat || maximum == unlimitedRepeat {
				maximum = unlimitedRepeat
			} else if high > maximum {
				maximum = high
			}
		}
		if minimum == int(^uint(0)>>1) {
			minimum = 0
		}
		return minimum, maximum
	case nodeRepeat:
		low, high := expressionWidth(value.children[0])
		return saturatedMultiply(low, value.minimum),
			saturatedMultiply(high, value.maximum)
	default:
		return 0, unlimitedRepeat
	}
}

type opcode uint8

const (
	opAccept opcode = iota
	opRune
	opAny
	opCategory
	opClass
	opSplit
	opSave
	opAnchor
	opBackreference
	opRepeat
	opRepeatEnd
	opLook
	opConditional
	opAtomicStart
	opAtomicEnd
)

type instruction struct {
	operation  opcode
	next       int
	alternate  int
	character  rune
	category   category
	class      *characterClass
	flags      uint32
	slot       int
	minimum    int
	maximum    int
	lazy       bool
	positive   bool
	lookbehind bool
	anchor     anchor
	nested     *program
}

type program struct {
	code        []instruction
	start       int
	groups      int
	flags       uint32
	byteMode    bool
	names       []namedGroup
	repeatSlots int
	atomicSlots int
}

type compiler struct {
	code        []instruction
	repeatSlots int
	atomicSlots int
	groups      int
	byteMode    bool
	flags       uint32
}

func (c *compiler) append(value instruction) int {
	index := len(c.code)
	c.code = append(c.code, value)
	return index
}

func (c *compiler) translate(value *expression, continuation int) int {
	switch value.kind {
	case nodeEmpty:
		return continuation
	case nodeLiteral:
		return c.append(instruction{
			operation: opRune, next: continuation,
			character: value.character, flags: value.flags,
		})
	case nodeAny:
		return c.append(instruction{
			operation: opAny, next: continuation, flags: value.flags,
		})
	case nodeCategory:
		return c.append(instruction{
			operation: opCategory, next: continuation,
			category: value.category, flags: value.flags,
		})
	case nodeClass:
		return c.append(instruction{
			operation: opClass, next: continuation,
			class: value.class, flags: value.flags,
		})
	case nodeSequence:
		for index := len(value.children) - 1; index >= 0; index-- {
			continuation = c.translate(value.children[index], continuation)
		}
		return continuation
	case nodeAlternation:
		if len(value.children) == 0 {
			return continuation
		}
		current := c.translate(value.children[len(value.children)-1], continuation)
		for index := len(value.children) - 2; index >= 0; index-- {
			first := c.translate(value.children[index], continuation)
			current = c.append(instruction{
				operation: opSplit,
				next:      first,
				alternate: current,
			})
		}
		return current
	case nodeGroup:
		end := c.append(instruction{
			operation: opSave,
			next:      continuation,
			slot:      value.group*2 + 1,
		})
		body := c.translate(value.children[0], end)
		return c.append(instruction{
			operation: opSave,
			next:      body,
			slot:      value.group * 2,
		})
	case nodeRepeat:
		slot := c.repeatSlots
		c.repeatSlots++
		head := c.append(instruction{
			operation: opRepeat,
			next:      continuation,
			slot:      slot,
			minimum:   value.minimum,
			maximum:   value.maximum,
			lazy:      value.lazy,
		})
		tail := c.append(instruction{
			operation: opRepeatEnd,
			next:      head,
			slot:      slot,
		})
		c.code[head].alternate = c.translate(value.children[0], tail)
		return head
	case nodeBackreference:
		return c.append(instruction{
			operation: opBackreference,
			next:      continuation,
			slot:      value.group,
			flags:     value.flags,
		})
	case nodeAnchor:
		return c.append(instruction{
			operation: opAnchor,
			next:      continuation,
			anchor:    value.anchor,
			flags:     value.flags,
		})
	case nodeLook:
		nested := compiler{
			groups:   c.groups,
			byteMode: c.byteMode,
			flags:    c.flags,
		}
		accept := nested.append(instruction{operation: opAccept})
		begin := nested.translate(value.children[0], accept)
		compiled := &program{
			code:        nested.code,
			start:       begin,
			groups:      c.groups,
			byteMode:    c.byteMode,
			flags:       c.flags,
			repeatSlots: nested.repeatSlots,
			atomicSlots: nested.atomicSlots,
		}
		return c.append(instruction{
			operation:  opLook,
			next:       continuation,
			positive:   value.positive,
			lookbehind: value.lookbehind,
			minimum:    value.minimum,
			nested:     compiled,
		})
	case nodeConditional:
		yes := c.translate(value.children[0], continuation)
		no := c.translate(value.children[1], continuation)
		return c.append(instruction{
			operation: opConditional,
			next:      yes,
			alternate: no,
			slot:      value.group,
		})
	case nodeAtomic:
		slot := c.atomicSlots
		c.atomicSlots++
		end := c.append(instruction{
			operation: opAtomicEnd,
			next:      continuation,
			slot:      slot,
		})
		body := c.translate(value.children[0], end)
		return c.append(instruction{
			operation: opAtomicStart,
			next:      body,
			slot:      slot,
		})
	default:
		return continuation
	}
}

func compileProgram(
	source []rune,
	flags uint32,
	byteMode bool,
	namedRunes map[int]rune,
) (*program, *failure) {
	known := flagTemplate | flagIgnoreCase | flagLocale | flagMultiline |
		flagDotAll | flagUnicode | flagVerbose | flagDebug | flagASCII
	if flags&^known != 0 {
		return nil, &failure{
			message:  "invalid regular expression flags",
			position: 0,
			kind:     compileInvalid,
		}
	}
	p := parser{
		source:      source,
		flags:       flags,
		byteMode:    byteMode,
		groupByName: make(map[string]int),
		namedRunes:  namedRunes,
	}
	tree, err := p.parse()
	if err != nil {
		return nil, err
	}
	c := compiler{
		groups:   p.groupCount,
		byteMode: byteMode,
		flags:    p.flags,
	}
	accept := c.append(instruction{operation: opAccept})
	end := c.append(instruction{operation: opSave, next: accept, slot: 1})
	body := c.translate(tree, end)
	start := c.append(instruction{operation: opSave, next: body, slot: 0})
	return &program{
		code:        c.code,
		start:       start,
		groups:      p.groupCount,
		flags:       p.flags,
		byteMode:    byteMode,
		names:       append([]namedGroup(nil), p.namedGroups...),
		repeatSlots: c.repeatSlots,
		atomicSlots: c.atomicSlots,
	}, nil
}

type subject struct {
	characters []C.uint32_t
	lowercase  []C.uint32_t
	traits     []C.uint8_t
	byteMode   bool
	beginning  int
	end        int
}

func (s *subject) character(index int) rune {
	return rune(s.characters[index])
}

func foldedRune(value rune, flags uint32, byteMode bool) rune {
	if flags&flagIgnoreCase == 0 {
		return value
	}
	if flags&flagASCII != 0 || (byteMode && flags&flagLocale == 0) {
		if value >= 'A' && value <= 'Z' {
			return value + ('a' - 'A')
		}
		return value
	}
	switch value {
	case '\u0130', '\u0131':
		return 'i'
	case '\u017f':
		return 's'
	}
	return unicode.ToLower(value)
}

func (s *subject) folded(index int, flags uint32) rune {
	value := s.character(index)
	if flags&flagIgnoreCase == 0 {
		return value
	}
	if flags&flagASCII != 0 || (s.byteMode && flags&flagLocale == 0) {
		return foldedRune(value, flags|flagASCII, s.byteMode)
	}
	return rune(s.lowercase[index])
}

func (s *subject) categoryAt(kind category, index int, flags uint32) bool {
	bits := uint8(s.traits[index])
	var present bool
	switch kind {
	case categoryDigit, categoryNotDigit:
		if s.byteMode || flags&flagASCII != 0 {
			present = bits&traitASCIIDigit != 0
		} else {
			present = bits&traitUnicodeDigit != 0
		}
	case categorySpace, categoryNotSpace:
		if s.byteMode || flags&flagASCII != 0 {
			present = bits&traitASCIISpace != 0
		} else {
			present = bits&traitUnicodeSpace != 0
		}
	case categoryWord, categoryNotWord:
		switch {
		case s.byteMode && flags&flagLocale != 0:
			present = bits&traitLocaleWord != 0
		case s.byteMode || flags&flagASCII != 0:
			present = bits&traitASCIIWord != 0
		default:
			present = bits&traitUnicodeWord != 0
		}
	}
	switch kind {
	case categoryNotDigit, categoryNotSpace, categoryNotWord:
		return !present
	default:
		return present
	}
}

func (s *subject) classAt(value *characterClass, index int, flags uint32) bool {
	current := s.character(index)
	matched := false
	for _, item := range value.items {
		if item.category != 0 {
			if s.categoryAt(item.category, index, flags) {
				matched = true
				break
			}
			continue
		}
		if current >= item.first && current <= item.last {
			matched = true
			break
		}
		if flags&flagIgnoreCase != 0 {
			fold := s.folded(index, flags)
			if item.first == item.last {
				if foldedRune(item.first, flags, s.byteMode) == fold {
					matched = true
					break
				}
			} else {
				for candidate := item.first; candidate <= item.last; candidate++ {
					if foldedRune(candidate, flags, s.byteMode) == fold {
						matched = true
						break
					}
					if candidate == unicode.MaxRune {
						break
					}
				}
				if matched {
					break
				}
			}
		}
	}
	if value.negated {
		return !matched
	}
	return matched
}

type repeatFrame struct {
	count  int
	start  int
	active bool
	empty  bool
}

type thread struct {
	ip        int
	position  int
	lastIndex int
	spans     []int
	repeats   []repeatFrame
	atomics   []int
}

func (t thread) clone() thread {
	return thread{
		ip:        t.ip,
		position:  t.position,
		lastIndex: t.lastIndex,
		spans:     append([]int(nil), t.spans...),
		repeats:   append([]repeatFrame(nil), t.repeats...),
		atomics:   append([]int(nil), t.atomics...),
	}
}

func newThread(value *program, beginning int, captures []int) thread {
	spans := make([]int, 2*(value.groups+1))
	for index := range spans {
		spans[index] = -1
	}
	if captures != nil {
		copy(spans, captures)
	}
	atomics := make([]int, value.atomicSlots)
	for index := range atomics {
		atomics[index] = -1
	}
	return thread{
		ip:        value.start,
		position:  beginning,
		lastIndex: -1,
		spans:     spans,
		repeats:   make([]repeatFrame, value.repeatSlots),
		atomics:   atomics,
	}
}

func (s *subject) anchorAt(value anchor, position int, flags uint32) bool {
	switch value {
	case anchorAbsoluteBeginning:
		return position == 0
	case anchorAbsoluteEnd:
		return position == s.end
	case anchorBeginning:
		return position == 0 ||
			(flags&flagMultiline != 0 && position > 0 &&
				s.character(position-1) == '\n')
	case anchorEnd:
		return position == s.end ||
			(position+1 == s.end && position < s.end &&
				s.character(position) == '\n') ||
			(flags&flagMultiline != 0 && position < s.end &&
				s.character(position) == '\n')
	case anchorWordBoundary, anchorNotWordBoundary:
		before := position > 0 && s.categoryAt(categoryWord, position-1, flags)
		after := position < s.end && s.categoryAt(categoryWord, position, flags)
		boundary := before != after
		if value == anchorNotWordBoundary {
			return !boundary
		}
		return boundary
	default:
		return false
	}
}

func (s *subject) backreferenceAt(t *thread, group int, flags uint32) bool {
	start := t.spans[group*2]
	end := t.spans[group*2+1]
	if start < 0 || end < start || end-start > s.end-t.position {
		return false
	}
	for offset := 0; offset < end-start; offset++ {
		left := start + offset
		right := t.position + offset
		if flags&flagIgnoreCase == 0 {
			if s.character(left) != s.character(right) {
				return false
			}
		} else if s.folded(left, flags) != s.folded(right, flags) {
			return false
		}
	}
	t.position += end - start
	return true
}

func (value *program) executeAt(
	input *subject,
	start int,
	requireEnd bool,
	rejectEmpty bool,
	initialCaptures []int,
) (thread, bool) {
	current := newThread(value, start, initialCaptures)
	backtracks := make([]thread, 0, 8)
	failed := func() bool {
		if len(backtracks) == 0 {
			return false
		}
		last := len(backtracks) - 1
		current = backtracks[last]
		backtracks = backtracks[:last]
		return true
	}
	for {
		if current.ip < 0 || current.ip >= len(value.code) {
			if !failed() {
				return thread{}, false
			}
			continue
		}
		op := value.code[current.ip]
		switch op.operation {
		case opAccept:
			if (requireEnd && current.position != input.end) ||
				(rejectEmpty && current.position == start) {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			return current, true
		case opRune:
			if current.position >= input.end {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			actual := input.character(current.position)
			if op.flags&flagIgnoreCase != 0 {
				actual = input.folded(current.position, op.flags)
			}
			expected := foldedRune(op.character, op.flags, value.byteMode)
			if actual != expected {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			current.position++
			current.ip = op.next
		case opAny:
			if current.position >= input.end ||
				(op.flags&flagDotAll == 0 &&
					input.character(current.position) == '\n') {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			current.position++
			current.ip = op.next
		case opCategory:
			if current.position >= input.end ||
				!input.categoryAt(op.category, current.position, op.flags) {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			current.position++
			current.ip = op.next
		case opClass:
			if current.position >= input.end ||
				!input.classAt(op.class, current.position, op.flags) {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			current.position++
			current.ip = op.next
		case opSplit:
			alternative := current.clone()
			alternative.ip = op.alternate
			backtracks = append(backtracks, alternative)
			current.ip = op.next
		case opSave:
			current.spans[op.slot] = current.position
			if op.slot > 1 && op.slot%2 == 1 {
				current.lastIndex = op.slot / 2
			}
			current.ip = op.next
		case opAnchor:
			if !input.anchorAt(op.anchor, current.position, op.flags) {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			current.ip = op.next
		case opBackreference:
			if !input.backreferenceAt(&current, op.slot, op.flags) {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			current.ip = op.next
		case opRepeat:
			frame := current.repeats[op.slot]
			if !frame.active {
				frame = repeatFrame{active: true, start: current.position}
				current.repeats[op.slot] = frame
			}
			canExit := frame.count >= op.minimum
			canEnter := (op.maximum == unlimitedRepeat ||
				frame.count < op.maximum) &&
				(!frame.empty || frame.count < op.minimum)
			if !canExit && !canEnter {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			if canExit && canEnter {
				alternative := current.clone()
				if op.lazy {
					alternative.repeats[op.slot].start = alternative.position
					alternative.ip = op.alternate
					current.repeats[op.slot] = repeatFrame{}
					current.ip = op.next
				} else {
					alternative.repeats[op.slot] = repeatFrame{}
					alternative.ip = op.next
					current.repeats[op.slot].start = current.position
					current.ip = op.alternate
				}
				backtracks = append(backtracks, alternative)
			} else if canEnter {
				current.repeats[op.slot].start = current.position
				current.ip = op.alternate
			} else {
				current.repeats[op.slot] = repeatFrame{}
				current.ip = op.next
			}
		case opRepeatEnd:
			frame := &current.repeats[op.slot]
			frame.count++
			frame.empty = current.position == frame.start
			current.ip = op.next
		case opLook:
			lookStart := current.position
			lookEnd := input.end
			if op.lookbehind {
				lookStart -= op.minimum
				lookEnd = current.position
			}
			matched := false
			var result thread
			if lookStart >= 0 {
				nestedInput := *input
				nestedInput.end = lookEnd
				result, matched = op.nested.executeAt(
					&nestedInput,
					lookStart,
					op.lookbehind,
					false,
					current.spans,
				)
			}
			if matched != op.positive {
				if !failed() {
					return thread{}, false
				}
				continue
			}
			if matched && op.positive {
				for index := 2; index < len(current.spans); index++ {
					current.spans[index] = result.spans[index]
				}
				if result.lastIndex >= 0 {
					current.lastIndex = result.lastIndex
				}
			}
			current.ip = op.next
		case opConditional:
			if current.spans[op.slot*2] >= 0 &&
				current.spans[op.slot*2+1] >= 0 {
				current.ip = op.next
			} else {
				current.ip = op.alternate
			}
		case opAtomicStart:
			current.atomics[op.slot] = len(backtracks)
			current.ip = op.next
		case opAtomicEnd:
			mark := current.atomics[op.slot]
			if mark >= 0 && mark <= len(backtracks) {
				backtracks = backtracks[:mark]
			}
			current.atomics[op.slot] = -1
			current.ip = op.next
		default:
			if !failed() {
				return thread{}, false
			}
		}
	}
}

func (value *program) run(
	input *subject,
	anchored bool,
	fullmatch bool,
	rejectFirstEmpty bool,
) (thread, bool) {
	for beginning := input.beginning; beginning <= input.end; beginning++ {
		reject := rejectFirstEmpty && beginning == input.beginning
		result, matched := value.executeAt(
			input,
			beginning,
			fullmatch,
			reject,
			nil,
		)
		if matched {
			return result, true
		}
		if anchored || fullmatch {
			break
		}
	}
	return thread{}, false
}

func programFromHandle(raw C.uint64_t) (result *program, ok bool) {
	defer func() {
		if recover() != nil {
			result = nil
			ok = false
		}
	}()
	if raw == 0 {
		return nil, false
	}
	result, ok = cgo.Handle(uintptr(raw)).Value().(*program)
	return result, ok && result != nil
}

func setFailure(
	message **C.char,
	position *C.int64_t,
	kind *C.int,
	err *failure,
) {
	if message != nil {
		*message = C.CString(err.message)
	}
	if position != nil {
		*position = C.int64_t(err.position)
	}
	if kind != nil {
		*kind = C.int(err.kind)
	}
}

//export rebar_go_compile
func rebar_go_compile(
	source *C.uint32_t,
	length C.size_t,
	flags C.uint32_t,
	byteMode C.uint8_t,
	namedPositions *C.size_t,
	namedValues *C.uint32_t,
	namedCount C.size_t,
	errorMessage **C.char,
	errorPosition *C.int64_t,
	errorKind *C.int,
) (result C.uint64_t) {
	defer func() {
		if recovered := recover(); recovered != nil {
			setFailure(errorMessage, errorPosition, errorKind, &failure{
				message:  "Go regular-expression compiler failed safely",
				position: 0,
				kind:     compileLimit,
			})
			result = 0
		}
	}()
	maximum := uint64(^uint(0) >> 1)
	if uint64(length) > maximum || uint64(namedCount) > maximum {
		setFailure(errorMessage, errorPosition, errorKind, &failure{
			message:  "regular-expression input is too large",
			position: 0,
			kind:     compileLimit,
		})
		return 0
	}
	count := int(length)
	characters := make([]rune, count)
	if count != 0 {
		if source == nil {
			setFailure(errorMessage, errorPosition, errorKind, &failure{
				message:  "missing regular-expression source",
				position: 0,
				kind:     compileLimit,
			})
			return 0
		}
		values := unsafe.Slice(source, count)
		for index, value := range values {
			if uint32(value) > unicode.MaxRune ||
				(byteMode != 0 && uint32(value) > 255) {
				setFailure(errorMessage, errorPosition, errorKind, &failure{
					message:  "invalid regular-expression character",
					position: index,
					kind:     compileInvalid,
				})
				return 0
			}
			characters[index] = rune(value)
		}
	}
	resolved := make(map[int]rune, int(namedCount))
	if namedCount != 0 {
		if namedPositions == nil || namedValues == nil {
			setFailure(errorMessage, errorPosition, errorKind, &failure{
				message:  "missing resolved Unicode character names",
				position: 0,
				kind:     compileLimit,
			})
			return 0
		}
		positions := unsafe.Slice(namedPositions, int(namedCount))
		values := unsafe.Slice(namedValues, int(namedCount))
		for index, position := range positions {
			if uint64(position) >= uint64(length) ||
				uint32(values[index]) > unicode.MaxRune {
				setFailure(errorMessage, errorPosition, errorKind, &failure{
					message:  "invalid resolved Unicode character name",
					position: 0,
					kind:     compileLimit,
				})
				return 0
			}
			resolved[int(position)] = rune(values[index])
		}
	}
	value, err := compileProgram(characters, uint32(flags), byteMode != 0, resolved)
	if err != nil {
		setFailure(errorMessage, errorPosition, errorKind, err)
		return 0
	}
	return C.uint64_t(cgo.NewHandle(value))
}

//export rebar_go_release
func rebar_go_release(raw C.uint64_t) (result C.int) {
	defer func() {
		if recover() != nil {
			result = -1
		}
	}()
	if raw == 0 {
		return -1
	}
	cgo.Handle(uintptr(raw)).Delete()
	return 0
}

//export rebar_go_group_count
func rebar_go_group_count(raw C.uint64_t) C.size_t {
	value, ok := programFromHandle(raw)
	if !ok {
		return 0
	}
	return C.size_t(value.groups)
}

//export rebar_go_flags
func rebar_go_flags(raw C.uint64_t) C.uint32_t {
	value, ok := programFromHandle(raw)
	if !ok {
		return 0
	}
	return C.uint32_t(value.flags)
}

//export rebar_go_name_count
func rebar_go_name_count(raw C.uint64_t) C.size_t {
	value, ok := programFromHandle(raw)
	if !ok {
		return 0
	}
	return C.size_t(len(value.names))
}

//export rebar_go_name_group
func rebar_go_name_group(raw C.uint64_t, index C.size_t) C.size_t {
	value, ok := programFromHandle(raw)
	if !ok || uint64(index) >= uint64(len(value.names)) {
		return 0
	}
	return C.size_t(value.names[int(index)].number)
}

//export rebar_go_name_length
func rebar_go_name_length(raw C.uint64_t, index C.size_t) C.size_t {
	value, ok := programFromHandle(raw)
	if !ok || uint64(index) >= uint64(len(value.names)) {
		return 0
	}
	return C.size_t(len(value.names[int(index)].name))
}

//export rebar_go_copy_name
func rebar_go_copy_name(
	raw C.uint64_t,
	index C.size_t,
	destination *C.uint8_t,
	capacity C.size_t,
) C.size_t {
	value, ok := programFromHandle(raw)
	if !ok || uint64(index) >= uint64(len(value.names)) {
		return 0
	}
	name := value.names[int(index)].name
	if uint64(capacity) < uint64(len(name)) ||
		(len(name) != 0 && destination == nil) {
		return 0
	}
	if len(name) != 0 {
		target := unsafe.Slice(destination, len(name))
		for offset := range name {
			target[offset] = C.uint8_t(name[offset])
		}
	}
	return C.size_t(len(name))
}

//export rebar_go_execute
func rebar_go_execute(
	raw C.uint64_t,
	characters *C.uint32_t,
	lowercase *C.uint32_t,
	traits *C.uint8_t,
	length C.size_t,
	beginning C.size_t,
	end C.size_t,
	anchored C.uint8_t,
	fullmatch C.uint8_t,
	rejectFirstEmpty C.uint8_t,
	spans *C.int64_t,
	spanCount C.size_t,
	lastIndex *C.int64_t,
) (result C.int) {
	defer func() {
		if recover() != nil {
			result = -2
		}
	}()
	value, ok := programFromHandle(raw)
	if !ok {
		return -1
	}
	maximum := uint64(^uint(0) >> 1)
	if uint64(length) > maximum || uint64(beginning) > uint64(length) ||
		uint64(end) > uint64(length) ||
		uint64(spanCount) != uint64(2*(value.groups+1)) ||
		lastIndex == nil ||
		(length != 0 && (characters == nil || lowercase == nil || traits == nil)) ||
		(spanCount != 0 && spans == nil) {
		return -1
	}
	input := subject{
		byteMode:  value.byteMode,
		beginning: int(beginning),
		end:       int(end),
	}
	if length != 0 {
		input.characters = unsafe.Slice(characters, int(length))
		input.lowercase = unsafe.Slice(lowercase, int(length))
		input.traits = unsafe.Slice(traits, int(length))
	}
	found, matched := value.run(
		&input,
		anchored != 0,
		fullmatch != 0,
		rejectFirstEmpty != 0,
	)
	if !matched {
		return 0
	}
	output := unsafe.Slice(spans, int(spanCount))
	for index, position := range found.spans {
		output[index] = C.int64_t(position)
	}
	*lastIndex = C.int64_t(found.lastIndex)
	return 1
}

func main() {}
