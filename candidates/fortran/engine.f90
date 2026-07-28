module rebar_fortran_engine
    use, intrinsic :: iso_c_binding, only: c_associated, c_f_pointer, c_int, &
        c_int8_t, c_int32_t, c_int64_t, c_loc, c_null_ptr, c_ptr, c_size_t
    implicit none
    private

    integer(c_int32_t), parameter :: flag_ignorecase = 2_c_int32_t
    integer(c_int32_t), parameter :: flag_locale = 4_c_int32_t
    integer(c_int32_t), parameter :: flag_multiline = 8_c_int32_t
    integer(c_int32_t), parameter :: flag_dotall = 16_c_int32_t
    integer(c_int32_t), parameter :: flag_unicode = 32_c_int32_t
    integer(c_int32_t), parameter :: flag_verbose = 64_c_int32_t
    integer(c_int32_t), parameter :: flag_ascii = 256_c_int32_t

    integer(c_int32_t), parameter :: node_empty = 0_c_int32_t
    integer(c_int32_t), parameter :: node_character = 1_c_int32_t
    integer(c_int32_t), parameter :: node_any = 2_c_int32_t
    integer(c_int32_t), parameter :: node_class = 3_c_int32_t
    integer(c_int32_t), parameter :: node_begin = 4_c_int32_t
    integer(c_int32_t), parameter :: node_end = 5_c_int32_t
    integer(c_int32_t), parameter :: node_absolute_begin = 6_c_int32_t
    integer(c_int32_t), parameter :: node_absolute_end = 7_c_int32_t
    integer(c_int32_t), parameter :: node_boundary = 8_c_int32_t
    integer(c_int32_t), parameter :: node_not_boundary = 9_c_int32_t
    integer(c_int32_t), parameter :: node_sequence = 10_c_int32_t
    integer(c_int32_t), parameter :: node_alternation = 11_c_int32_t
    integer(c_int32_t), parameter :: node_capture = 12_c_int32_t
    integer(c_int32_t), parameter :: node_reference = 13_c_int32_t
    integer(c_int32_t), parameter :: node_repeat = 14_c_int32_t
    integer(c_int32_t), parameter :: node_atomic = 15_c_int32_t

    integer(c_int32_t), parameter :: op_accept = 0_c_int32_t
    integer(c_int32_t), parameter :: op_character = 1_c_int32_t
    integer(c_int32_t), parameter :: op_any = 2_c_int32_t
    integer(c_int32_t), parameter :: op_class = 3_c_int32_t
    integer(c_int32_t), parameter :: op_begin = 4_c_int32_t
    integer(c_int32_t), parameter :: op_end = 5_c_int32_t
    integer(c_int32_t), parameter :: op_absolute_begin = 6_c_int32_t
    integer(c_int32_t), parameter :: op_absolute_end = 7_c_int32_t
    integer(c_int32_t), parameter :: op_boundary = 8_c_int32_t
    integer(c_int32_t), parameter :: op_not_boundary = 9_c_int32_t
    integer(c_int32_t), parameter :: op_jump = 10_c_int32_t
    integer(c_int32_t), parameter :: op_branch = 11_c_int32_t
    integer(c_int32_t), parameter :: op_capture = 12_c_int32_t
    integer(c_int32_t), parameter :: op_reference = 13_c_int32_t
    integer(c_int32_t), parameter :: op_repeat_enter = 14_c_int32_t
    integer(c_int32_t), parameter :: op_repeat_again = 15_c_int32_t
    integer(c_int32_t), parameter :: op_atomic_enter = 16_c_int32_t
    integer(c_int32_t), parameter :: op_atomic_leave = 17_c_int32_t

    integer(c_int), parameter :: error_none = 0_c_int
    integer(c_int), parameter :: error_memory = 1_c_int
    integer(c_int), parameter :: error_escape = 2_c_int
    integer(c_int), parameter :: error_parenthesis = 3_c_int
    integer(c_int), parameter :: error_class = 4_c_int
    integer(c_int), parameter :: error_repeat = 5_c_int
    integer(c_int), parameter :: error_group = 6_c_int
    integer(c_int), parameter :: error_extension = 7_c_int
    integer(c_int), parameter :: error_comment = 8_c_int
    integer(c_int), parameter :: error_overflow = 9_c_int
    integer(c_int), parameter :: error_unsupported = 10_c_int

    integer(c_int32_t), parameter :: category_digit = 1_c_int32_t
    integer(c_int32_t), parameter :: category_not_digit = 2_c_int32_t
    integer(c_int32_t), parameter :: category_space = 3_c_int32_t
    integer(c_int32_t), parameter :: category_not_space = 4_c_int32_t
    integer(c_int32_t), parameter :: category_word = 5_c_int32_t
    integer(c_int32_t), parameter :: category_not_word = 6_c_int32_t

    integer(c_int8_t), parameter :: trait_unicode_digit = 1_c_int8_t
    integer(c_int8_t), parameter :: trait_unicode_space = 2_c_int8_t
    integer(c_int8_t), parameter :: trait_unicode_word = 4_c_int8_t
    integer(c_int8_t), parameter :: trait_ascii_digit = 8_c_int8_t
    integer(c_int8_t), parameter :: trait_ascii_space = 16_c_int8_t
    integer(c_int8_t), parameter :: trait_ascii_word = 32_c_int8_t
    integer(c_int8_t), parameter :: trait_locale_word = 64_c_int8_t

    integer(c_int64_t), parameter :: unmatched = -1_c_int64_t
    integer(c_int64_t), parameter :: unlimited = huge(0_c_int64_t)

    type :: token_type
        integer(c_int32_t) :: character = 0_c_int32_t
        integer(c_int64_t) :: position = 0_c_int64_t
        logical :: escaped = .false.
        logical :: finished = .false.
    end type token_type

    type :: syntax_node
        integer(c_int32_t) :: kind = node_empty
        integer(c_int32_t) :: flags = 0_c_int32_t
        integer(c_int32_t) :: value = 0_c_int32_t
        integer(c_int32_t), allocatable :: children(:)
        integer(c_int64_t) :: minimum = 0_c_int64_t
        integer(c_int64_t) :: maximum = unlimited
        logical :: lazy = .false.
        logical :: possessive = .false.
    end type syntax_node

    type :: class_type
        integer(c_int32_t), allocatable :: first(:)
        integer(c_int32_t), allocatable :: last(:)
        integer(c_int32_t), allocatable :: categories(:)
        logical :: complemented = .false.
    end type class_type

    type :: group_name_type
        integer(c_int32_t), allocatable :: characters(:)
        integer(c_int32_t) :: number = 0_c_int32_t
    end type group_name_type

    type :: repeat_type
        integer(c_int64_t) :: minimum = 0_c_int64_t
        integer(c_int64_t) :: maximum = unlimited
        logical :: lazy = .false.
    end type repeat_type

    type :: instruction_type
        integer(c_int32_t) :: opcode = op_accept
        integer(c_int32_t) :: first = 0_c_int32_t
        integer(c_int32_t) :: second = 0_c_int32_t
        integer(c_int32_t) :: flags = 0_c_int32_t
        integer(c_int32_t) :: character = 0_c_int32_t
    end type instruction_type

    type :: engine_state
        integer(c_int32_t), allocatable :: pattern(:)
        integer(c_int32_t), allocatable :: folded_pattern(:)
        integer(c_int8_t), allocatable :: pattern_traits(:)
        type(syntax_node), allocatable :: nodes(:)
        type(class_type), allocatable :: classes(:)
        type(group_name_type), allocatable :: names(:)
        type(repeat_type), allocatable :: repeats(:)
        type(instruction_type), allocatable :: instructions(:)
        integer(c_int32_t) :: flags = 0_c_int32_t
        integer(c_int32_t) :: groups = 0_c_int32_t
        logical :: bytes = .false.
    end type engine_state

    type :: parser_state
        type(engine_state), pointer :: engine => null()
        integer(c_int64_t) :: position = 0_c_int64_t
        integer(c_int64_t) :: length = 0_c_int64_t
        integer(c_int64_t) :: error_position = unmatched
        integer(c_int) :: status = error_none
    end type parser_state

    type :: execution_state
        integer(c_int32_t) :: pc = 1_c_int32_t
        integer(c_int64_t) :: position = 0_c_int64_t
        integer(c_int64_t) :: last_group = unmatched
        integer(c_int64_t), allocatable :: captures(:)
        integer(c_int64_t), allocatable :: repeat_count(:)
        integer(c_int64_t), allocatable :: repeat_position(:)
        logical, allocatable :: repeat_active(:)
        logical, allocatable :: repeat_stalled(:)
        integer(c_int32_t), allocatable :: barriers(:)
    end type execution_state

    public :: rebar_fortran_compile
    public :: rebar_fortran_destroy
    public :: rebar_fortran_group_count
    public :: rebar_fortran_effective_flags
    public :: rebar_fortran_name_count
    public :: rebar_fortran_name_length
    public :: rebar_fortran_name_group
    public :: rebar_fortran_copy_name
    public :: rebar_fortran_execute

    interface
        integer(c_int32_t) function rebar_fortran_unicode_case_key(character) &
            bind(C, name="rebar_fortran_unicode_case_key")
            import :: c_int32_t
            integer(c_int32_t), value, intent(in) :: character
        end function rebar_fortran_unicode_case_key

        integer(c_int32_t) function rebar_fortran_locale_case_key(character) &
            bind(C, name="rebar_fortran_locale_case_key")
            import :: c_int32_t
            integer(c_int32_t), value, intent(in) :: character
        end function rebar_fortran_locale_case_key

        integer(c_int32_t) function rebar_fortran_locale_is_word(character) &
            bind(C, name="rebar_fortran_locale_is_word")
            import :: c_int32_t
            integer(c_int32_t), value, intent(in) :: character
        end function rebar_fortran_locale_is_word
    end interface

contains

    pure logical function ascii_digit(character) result(value)
        integer(c_int32_t), intent(in) :: character
        value = character >= 48_c_int32_t .and. character <= 57_c_int32_t
    end function ascii_digit

    pure logical function ascii_letter(character) result(value)
        integer(c_int32_t), intent(in) :: character
        value = (character >= 65_c_int32_t .and. character <= 90_c_int32_t) .or. &
                (character >= 97_c_int32_t .and. character <= 122_c_int32_t)
    end function ascii_letter

    pure logical function ascii_identifier(character, first) result(value)
        integer(c_int32_t), intent(in) :: character
        logical, intent(in) :: first
        value = character == 95_c_int32_t .or. ascii_letter(character)
        if (.not. first) value = value .or. ascii_digit(character)
    end function ascii_identifier

    pure logical function is_verbose_space(character) result(value)
        integer(c_int32_t), intent(in) :: character
        value = character == 32_c_int32_t .or. &
                (character >= 9_c_int32_t .and. character <= 13_c_int32_t)
    end function is_verbose_space

    subroutine set_error(parser, code, position)
        type(parser_state), intent(inout) :: parser
        integer(c_int), intent(in) :: code
        integer(c_int64_t), intent(in) :: position
        if (parser%status == error_none) then
            parser%status = code
            parser%error_position = position
        end if
    end subroutine set_error

    pure integer(c_int32_t) function raw_character(parser, offset) result(character)
        type(parser_state), intent(in) :: parser
        integer(c_int64_t), intent(in) :: offset
        integer(c_int64_t) :: index
        index = parser%position + offset
        if (index < 0_c_int64_t .or. index >= parser%length) then
            character = 0_c_int32_t
        else
            character = parser%engine%pattern(int(index + 1_c_int64_t))
        end if
    end function raw_character

    subroutine raw_token(parser, token)
        type(parser_state), intent(inout) :: parser
        type(token_type), intent(out) :: token
        token = token_type()
        token%position = parser%position
        if (parser%position >= parser%length) then
            token%finished = .true.
            return
        end if
        token%character = raw_character(parser, 0_c_int64_t)
        parser%position = parser%position + 1_c_int64_t
        if (token%character /= 92_c_int32_t) return
        token%escaped = .true.
        if (parser%position >= parser%length) then
            call set_error(parser, error_escape, token%position)
            token%finished = .true.
            return
        end if
        token%character = raw_character(parser, 0_c_int64_t)
        parser%position = parser%position + 1_c_int64_t
    end subroutine raw_token

    subroutine next_token(parser, flags, token)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(in) :: flags
        type(token_type), intent(out) :: token
        integer(c_int32_t) :: character
        if (iand(flags, flag_verbose) /= 0_c_int32_t) then
            do while (parser%position < parser%length)
                character = raw_character(parser, 0_c_int64_t)
                if (is_verbose_space(character)) then
                    parser%position = parser%position + 1_c_int64_t
                    cycle
                end if
                if (character /= 35_c_int32_t) exit
                parser%position = parser%position + 1_c_int64_t
                do while (parser%position < parser%length)
                    call raw_token(parser, token)
                    if (parser%status /= error_none) return
                    if (.not. token%escaped .and. token%character == 10_c_int32_t) exit
                end do
            end do
        end if
        call raw_token(parser, token)
    end subroutine next_token

    subroutine peek_token(parser, flags, token)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(in) :: flags
        type(token_type), intent(out) :: token
        integer(c_int64_t) :: previous
        previous = parser%position
        call next_token(parser, flags, token)
        parser%position = previous
    end subroutine peek_token

    subroutine add_integer(values, item, status)
        integer(c_int32_t), allocatable, intent(inout) :: values(:)
        integer(c_int32_t), intent(in) :: item
        integer(c_int), intent(inout) :: status
        integer(c_int32_t), allocatable :: expanded(:)
        integer :: count, allocation
        if (status /= error_none) return
        count = 0
        if (allocated(values)) count = size(values)
        allocate(expanded(count + 1), stat=allocation)
        if (allocation /= 0) then
            status = error_memory
            return
        end if
        if (count /= 0) expanded(:count) = values
        expanded(count + 1) = item
        call move_alloc(expanded, values)
    end subroutine add_integer

    integer(c_int32_t) function add_node(parser, kind, flags) result(index)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(in) :: kind, flags
        type(syntax_node), allocatable :: expanded(:)
        integer :: count, allocation
        index = 0_c_int32_t
        if (parser%status /= error_none) return
        count = 0
        if (allocated(parser%engine%nodes)) count = size(parser%engine%nodes)
        if (int(count, c_int64_t) >= int(huge(0_c_int32_t), c_int64_t)) then
            call set_error(parser, error_overflow, parser%position)
            return
        end if
        allocate(expanded(count + 1), stat=allocation)
        if (allocation /= 0) then
            call set_error(parser, error_memory, parser%position)
            return
        end if
        if (count /= 0) expanded(:count) = parser%engine%nodes
        expanded(count + 1)%kind = kind
        expanded(count + 1)%flags = flags
        call move_alloc(expanded, parser%engine%nodes)
        index = int(count + 1, c_int32_t)
    end function add_node

    subroutine add_child(parser, parent, child)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(in) :: parent, child
        if (parser%status /= error_none .or. parent <= 0_c_int32_t) return
        call add_integer(parser%engine%nodes(parent)%children, child, parser%status)
        if (parser%status /= error_none .and. parser%error_position == unmatched) then
            parser%error_position = parser%position
        end if
    end subroutine add_child

    integer(c_int32_t) function add_class(parser) result(index)
        type(parser_state), intent(inout) :: parser
        type(class_type), allocatable :: expanded(:)
        integer :: count, allocation
        index = 0_c_int32_t
        count = 0
        if (allocated(parser%engine%classes)) count = size(parser%engine%classes)
        allocate(expanded(count + 1), stat=allocation)
        if (allocation /= 0) then
            call set_error(parser, error_memory, parser%position)
            return
        end if
        if (count /= 0) expanded(:count) = parser%engine%classes
        call move_alloc(expanded, parser%engine%classes)
        index = int(count + 1, c_int32_t)
    end function add_class

    subroutine class_range(parser, index, first, last)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(in) :: index, first, last
        if (parser%status /= error_none) return
        call add_integer(parser%engine%classes(index)%first, first, parser%status)
        call add_integer(parser%engine%classes(index)%last, last, parser%status)
        if (parser%status /= error_none .and. parser%error_position == unmatched) then
            parser%error_position = parser%position
        end if
    end subroutine class_range

    integer(c_int32_t) function add_name(parser, characters, group) result(index)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(in) :: characters(:)
        integer(c_int32_t), intent(in) :: group
        type(group_name_type), allocatable :: expanded(:)
        integer :: count, allocation, item
        index = 0_c_int32_t
        count = 0
        if (allocated(parser%engine%names)) count = size(parser%engine%names)
        do item = 1, count
            if (size(parser%engine%names(item)%characters) == size(characters)) then
                if (all(parser%engine%names(item)%characters == characters)) then
                    call set_error(parser, error_group, parser%position)
                    return
                end if
            end if
        end do
        allocate(expanded(count + 1), stat=allocation)
        if (allocation /= 0) then
            call set_error(parser, error_memory, parser%position)
            return
        end if
        if (count /= 0) expanded(:count) = parser%engine%names
        expanded(count + 1)%characters = characters
        expanded(count + 1)%number = group
        call move_alloc(expanded, parser%engine%names)
        index = int(count + 1, c_int32_t)
    end function add_name

    integer(c_int32_t) function named_group(parser, characters) result(number)
        type(parser_state), intent(in) :: parser
        integer(c_int32_t), intent(in) :: characters(:)
        integer :: item
        number = 0_c_int32_t
        if (.not. allocated(parser%engine%names)) return
        do item = 1, size(parser%engine%names)
            if (size(parser%engine%names(item)%characters) /= size(characters)) cycle
            if (all(parser%engine%names(item)%characters == characters)) then
                number = parser%engine%names(item)%number
                return
            end if
        end do
    end function named_group

    integer(c_int32_t) function category_from_escape(character) result(category)
        integer(c_int32_t), intent(in) :: character
        select case (character)
        case (100_c_int32_t)
            category = category_digit
        case (68_c_int32_t)
            category = category_not_digit
        case (115_c_int32_t)
            category = category_space
        case (83_c_int32_t)
            category = category_not_space
        case (119_c_int32_t)
            category = category_word
        case (87_c_int32_t)
            category = category_not_word
        case default
            category = 0_c_int32_t
        end select
    end function category_from_escape

    integer(c_int32_t) function hex_value(character) result(value)
        integer(c_int32_t), intent(in) :: character
        select case (character)
        case (48_c_int32_t:57_c_int32_t)
            value = character - 48_c_int32_t
        case (65_c_int32_t:70_c_int32_t)
            value = character - 55_c_int32_t
        case (97_c_int32_t:102_c_int32_t)
            value = character - 87_c_int32_t
        case default
            value = -1_c_int32_t
        end select
    end function hex_value

    integer(c_int32_t) function read_hex(parser, count, opening) result(value)
        type(parser_state), intent(inout) :: parser
        integer, intent(in) :: count
        integer(c_int64_t), intent(in) :: opening
        integer :: item
        integer(c_int32_t) :: digit
        integer(c_int64_t) :: wide
        value = 0_c_int32_t
        wide = 0_c_int64_t
        do item = 1, count
            digit = hex_value(raw_character(parser, 0_c_int64_t))
            if (digit < 0_c_int32_t) then
                call set_error(parser, error_escape, opening)
                return
            end if
            wide = wide * 16_c_int64_t + int(digit, c_int64_t)
            parser%position = parser%position + 1_c_int64_t
        end do
        if (wide > int(z'10FFFF', c_int64_t)) then
            call set_error(parser, error_escape, opening)
            return
        end if
        value = int(wide, c_int32_t)
    end function read_hex

    integer(c_int32_t) function escaped_node(parser, flags, token, in_class) result(index)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(in) :: flags
        type(token_type), intent(in) :: token
        logical, intent(in) :: in_class
        integer(c_int32_t) :: category, character, number
        integer(c_int64_t) :: opening
        index = 0_c_int32_t
        opening = token%position
        category = category_from_escape(token%character)
        if (category /= 0_c_int32_t) then
            index = add_node(parser, node_class, flags)
            if (index /= 0_c_int32_t) then
                parser%engine%nodes(index)%value = add_class(parser)
                if (parser%status == error_none) then
                    call add_integer( &
                        parser%engine%classes(parser%engine%nodes(index)%value)%categories, &
                        category, parser%status)
                end if
            end if
            return
        end if

        if (.not. in_class) then
            select case (token%character)
            case (65_c_int32_t)
                index = add_node(parser, node_absolute_begin, flags)
                return
            case (90_c_int32_t, 122_c_int32_t)
                index = add_node(parser, node_absolute_end, flags)
                return
            case (98_c_int32_t)
                index = add_node(parser, node_boundary, flags)
                return
            case (66_c_int32_t)
                index = add_node(parser, node_not_boundary, flags)
                return
            end select
        end if

        character = token%character
        select case (token%character)
        case (97_c_int32_t)
            character = 7_c_int32_t
        case (98_c_int32_t)
            character = 8_c_int32_t
        case (102_c_int32_t)
            character = 12_c_int32_t
        case (110_c_int32_t)
            character = 10_c_int32_t
        case (114_c_int32_t)
            character = 13_c_int32_t
        case (116_c_int32_t)
            character = 9_c_int32_t
        case (118_c_int32_t)
            character = 11_c_int32_t
        case (120_c_int32_t)
            character = read_hex(parser, 2, opening)
        case (117_c_int32_t)
            if (parser%engine%bytes) then
                call set_error(parser, error_escape, opening)
                return
            end if
            character = read_hex(parser, 4, opening)
        case (85_c_int32_t)
            if (parser%engine%bytes) then
                call set_error(parser, error_escape, opening)
                return
            end if
            character = read_hex(parser, 8, opening)
        case (78_c_int32_t)
            call set_error(parser, error_unsupported, opening)
            return
        case (49_c_int32_t:57_c_int32_t)
            if (.not. in_class) then
                number = token%character - 48_c_int32_t
                if (ascii_digit(raw_character(parser, 0_c_int64_t))) then
                    number = number * 10_c_int32_t + &
                        raw_character(parser, 0_c_int64_t) - 48_c_int32_t
                    parser%position = parser%position + 1_c_int64_t
                end if
                if (number <= 0_c_int32_t .or. number > parser%engine%groups) then
                    call set_error(parser, error_group, opening + 1_c_int64_t)
                    return
                end if
                index = add_node(parser, node_reference, flags)
                if (index /= 0_c_int32_t) parser%engine%nodes(index)%value = number
                return
            end if
        case default
            if (ascii_letter(token%character)) then
                call set_error(parser, error_escape, opening)
                return
            end if
        end select
        if (parser%status /= error_none) return
        index = add_node(parser, node_character, flags)
        if (index /= 0_c_int32_t) parser%engine%nodes(index)%value = character
    end function escaped_node

    recursive integer(c_int32_t) function parse_alternation(parser, flags) result(index)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(inout) :: flags
        type(token_type) :: token
        integer(c_int32_t) :: branch, alternative
        index = parse_sequence(parser, flags)
        if (parser%status /= error_none) return
        call peek_token(parser, flags, token)
        if (parser%status /= error_none) return
        if (token%finished .or. token%escaped .or. token%character /= 124_c_int32_t) return
        alternative = add_node(parser, node_alternation, flags)
        call add_child(parser, alternative, index)
        do
            call peek_token(parser, flags, token)
            if (parser%status /= error_none) exit
            if (token%finished .or. token%escaped) exit
            if (token%character /= 124_c_int32_t) exit
            call next_token(parser, flags, token)
            branch = parse_sequence(parser, flags)
            call add_child(parser, alternative, branch)
        end do
        index = alternative
    end function parse_alternation

    recursive integer(c_int32_t) function parse_sequence(parser, flags) result(index)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(inout) :: flags
        type(token_type) :: token
        integer(c_int32_t) :: child, combined
        integer :: total
        combined = add_node(parser, node_sequence, flags)
        if (combined == 0_c_int32_t) then
            index = 0_c_int32_t
            return
        end if
        do
            call peek_token(parser, flags, token)
            if (parser%status /= error_none .or. token%finished) exit
            if (.not. token%escaped) then
                if (token%character == 124_c_int32_t .or. &
                    token%character == 41_c_int32_t) exit
                if (token%character == 42_c_int32_t .or. &
                    token%character == 43_c_int32_t .or. &
                    token%character == 63_c_int32_t) then
                    call set_error(parser, error_repeat, token%position)
                    exit
                end if
            end if
            child = parse_atom(parser, flags)
            if (parser%status /= error_none) exit
            if (child == 0_c_int32_t) cycle
            child = parse_repeat(parser, flags, child)
            if (parser%status /= error_none) exit
            call add_child(parser, combined, child)
        end do
        if (parser%status /= error_none) then
            index = 0_c_int32_t
            return
        end if
        total = 0
        if (allocated(parser%engine%nodes(combined)%children)) then
            total = size(parser%engine%nodes(combined)%children)
        end if
        if (total == 1) then
            index = parser%engine%nodes(combined)%children(1)
        else
            index = combined
        end if
    end function parse_sequence

    recursive integer(c_int32_t) function parse_atom(parser, flags) result(index)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(inout) :: flags
        type(token_type) :: token
        call next_token(parser, flags, token)
        index = 0_c_int32_t
        if (parser%status /= error_none .or. token%finished) return
        if (token%escaped) then
            index = escaped_node(parser, flags, token, .false.)
            return
        end if
        select case (token%character)
        case (46_c_int32_t)
            index = add_node(parser, node_any, flags)
        case (94_c_int32_t)
            index = add_node(parser, node_begin, flags)
        case (36_c_int32_t)
            index = add_node(parser, node_end, flags)
        case (91_c_int32_t)
            index = parse_character_class(parser, flags, token%position)
        case (40_c_int32_t)
            index = parse_group(parser, flags, token%position)
        case default
            index = add_node(parser, node_character, flags)
            if (index /= 0_c_int32_t) then
                parser%engine%nodes(index)%value = token%character
            end if
        end select
    end function parse_atom

    integer(c_int32_t) function parse_character_class(parser, flags, opening) result(index)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(in) :: flags
        integer(c_int64_t), intent(in) :: opening
        type(token_type) :: left, right
        integer(c_int32_t) :: klass, category
        logical :: first
        index = 0_c_int32_t
        klass = add_class(parser)
        if (parser%status /= error_none) return
        if (raw_character(parser, 0_c_int64_t) == 94_c_int32_t) then
            parser%engine%classes(klass)%complemented = .true.
            parser%position = parser%position + 1_c_int64_t
        end if
        first = .true.
        do while (parser%position < parser%length)
            if (.not. first .and. raw_character(parser, 0_c_int64_t) == 93_c_int32_t) then
                parser%position = parser%position + 1_c_int64_t
                index = add_node(parser, node_class, flags)
                if (index /= 0_c_int32_t) parser%engine%nodes(index)%value = klass
                return
            end if
            first = .false.
            call next_token(parser, 0_c_int32_t, left)
            if (parser%status /= error_none .or. left%finished) exit
            category = 0_c_int32_t
            if (left%escaped) category = category_from_escape(left%character)
            if (category /= 0_c_int32_t) then
                call add_integer(parser%engine%classes(klass)%categories, &
                    category, parser%status)
                cycle
            end if
            if (left%escaped) then
                index = escaped_node(parser, 0_c_int32_t, left, .true.)
                if (parser%status /= error_none) return
                left%character = parser%engine%nodes(index)%value
            end if
            if (raw_character(parser, 0_c_int64_t) == 45_c_int32_t .and. &
                raw_character(parser, 1_c_int64_t) /= 93_c_int32_t .and. &
                raw_character(parser, 1_c_int64_t) /= 0_c_int32_t) then
                parser%position = parser%position + 1_c_int64_t
                call next_token(parser, 0_c_int32_t, right)
                if (parser%status /= error_none .or. right%finished) exit
                if (right%escaped) then
                    if (category_from_escape(right%character) /= 0_c_int32_t) then
                        call set_error(parser, error_class, left%position)
                        return
                    end if
                    index = escaped_node(parser, 0_c_int32_t, right, .true.)
                    if (parser%status /= error_none) return
                    right%character = parser%engine%nodes(index)%value
                end if
                if (right%character < left%character) then
                    call set_error(parser, error_class, left%position)
                    return
                end if
                call class_range(parser, klass, left%character, right%character)
            else
                call class_range(parser, klass, left%character, left%character)
            end if
            if (parser%status /= error_none) return
        end do
        call set_error(parser, error_class, opening)
    end function parse_character_class

    subroutine parse_group_name(parser, name, opening)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), allocatable, intent(out) :: name(:)
        integer(c_int64_t), intent(in) :: opening
        integer(c_int32_t) :: character
        do while (parser%position < parser%length)
            character = raw_character(parser, 0_c_int64_t)
            if (character == 62_c_int32_t) exit
            if (.not. ascii_identifier(character, .not. allocated(name))) then
                call set_error(parser, error_group, opening)
                return
            end if
            call add_integer(name, character, parser%status)
            if (parser%status /= error_none) return
            parser%position = parser%position + 1_c_int64_t
        end do
        if (.not. allocated(name) .or. &
            raw_character(parser, 0_c_int64_t) /= 62_c_int32_t) then
            call set_error(parser, error_group, opening)
            return
        end if
        parser%position = parser%position + 1_c_int64_t
    end subroutine parse_group_name

    integer(c_int32_t) function flag_value(character) result(value)
        integer(c_int32_t), intent(in) :: character
        select case (character)
        case (105_c_int32_t)
            value = flag_ignorecase
        case (76_c_int32_t)
            value = flag_locale
        case (109_c_int32_t)
            value = flag_multiline
        case (115_c_int32_t)
            value = flag_dotall
        case (117_c_int32_t)
            value = flag_unicode
        case (120_c_int32_t)
            value = flag_verbose
        case (97_c_int32_t)
            value = flag_ascii
        case default
            value = 0_c_int32_t
        end select
    end function flag_value

    recursive integer(c_int32_t) function parse_group(parser, enclosing, opening) result(index)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(inout) :: enclosing
        integer(c_int64_t), intent(in) :: opening
        type(token_type) :: token
        integer(c_int32_t), allocatable :: name(:)
        integer(c_int32_t) :: local_flags, capture, body, bit
        logical :: capturing, atomic, removing
        index = 0_c_int32_t
        local_flags = enclosing
        capturing = .true.
        atomic = .false.

        if (raw_character(parser, 0_c_int64_t) == 63_c_int32_t) then
            parser%position = parser%position + 1_c_int64_t
            select case (raw_character(parser, 0_c_int64_t))
            case (58_c_int32_t)
                parser%position = parser%position + 1_c_int64_t
                capturing = .false.
            case (35_c_int32_t)
                parser%position = parser%position + 1_c_int64_t
                do
                    call raw_token(parser, token)
                    if (parser%status /= error_none) return
                    if (token%finished) then
                        call set_error(parser, error_comment, opening)
                        return
                    end if
                    if (.not. token%escaped .and. &
                        token%character == 41_c_int32_t) exit
                end do
                return
            case (62_c_int32_t)
                parser%position = parser%position + 1_c_int64_t
                capturing = .false.
                atomic = .true.
            case (80_c_int32_t)
                parser%position = parser%position + 1_c_int64_t
                if (raw_character(parser, 0_c_int64_t) /= 60_c_int32_t) then
                    call set_error(parser, error_unsupported, opening)
                    return
                end if
                parser%position = parser%position + 1_c_int64_t
                call parse_group_name(parser, name, opening)
                if (parser%status /= error_none) return
            case (61_c_int32_t, 33_c_int32_t, 60_c_int32_t, 40_c_int32_t)
                call set_error(parser, error_unsupported, opening)
                return
            case default
                capturing = .false.
                removing = .false.
                do
                    bit = flag_value(raw_character(parser, 0_c_int64_t))
                    if (bit /= 0_c_int32_t) then
                        if (removing) then
                            local_flags = iand(local_flags, not(bit))
                        else
                            local_flags = ior(local_flags, bit)
                        end if
                        parser%position = parser%position + 1_c_int64_t
                    else if (raw_character(parser, 0_c_int64_t) == 45_c_int32_t) then
                        if (removing) then
                            call set_error(parser, error_extension, opening)
                            return
                        end if
                        removing = .true.
                        parser%position = parser%position + 1_c_int64_t
                    else
                        exit
                    end if
                end do
                if (raw_character(parser, 0_c_int64_t) == 41_c_int32_t) then
                    if (opening /= 0_c_int64_t .or. removing) then
                        call set_error(parser, error_extension, opening)
                        return
                    end if
                    parser%position = parser%position + 1_c_int64_t
                    enclosing = local_flags
                    parser%engine%flags = local_flags
                    return
                end if
                if (raw_character(parser, 0_c_int64_t) /= 58_c_int32_t) then
                    call set_error(parser, error_extension, opening)
                    return
                end if
                parser%position = parser%position + 1_c_int64_t
            end select
        end if

        capture = 0_c_int32_t
        if (capturing) then
            if (parser%engine%groups == huge(0_c_int32_t)) then
                call set_error(parser, error_overflow, opening)
                return
            end if
            parser%engine%groups = parser%engine%groups + 1_c_int32_t
            capture = parser%engine%groups
            if (allocated(name)) then
                bit = add_name(parser, name, capture)
                if (parser%status /= error_none .or. bit == 0_c_int32_t) return
            end if
        end if

        body = parse_alternation(parser, local_flags)
        if (parser%status /= error_none) return
        call next_token(parser, local_flags, token)
        if (parser%status /= error_none) return
        if (token%finished .or. token%escaped .or. &
            token%character /= 41_c_int32_t) then
            call set_error(parser, error_parenthesis, opening)
            return
        end if
        if (capturing) then
            index = add_node(parser, node_capture, local_flags)
            if (index /= 0_c_int32_t) then
                parser%engine%nodes(index)%value = capture
                call add_child(parser, index, body)
            end if
        else if (atomic) then
            index = add_node(parser, node_atomic, local_flags)
            call add_child(parser, index, body)
        else
            index = body
        end if
    end function parse_group

    logical function read_bound(parser, value) result(present)
        type(parser_state), intent(inout) :: parser
        integer(c_int64_t), intent(out) :: value
        integer(c_int32_t) :: digit
        value = 0_c_int64_t
        present = ascii_digit(raw_character(parser, 0_c_int64_t))
        if (.not. present) return
        do while (ascii_digit(raw_character(parser, 0_c_int64_t)))
            digit = raw_character(parser, 0_c_int64_t) - 48_c_int32_t
            if (value > (unlimited - int(digit, c_int64_t)) / 10_c_int64_t) then
                call set_error(parser, error_overflow, parser%position)
                return
            end if
            value = value * 10_c_int64_t + int(digit, c_int64_t)
            parser%position = parser%position + 1_c_int64_t
        end do
    end function read_bound

    integer(c_int32_t) function parse_repeat(parser, flags, child) result(index)
        type(parser_state), intent(inout) :: parser
        integer(c_int32_t), intent(in) :: flags, child
        type(token_type) :: token
        integer(c_int64_t) :: previous, minimum, maximum
        logical :: exists
        index = child
        call peek_token(parser, flags, token)
        if (parser%status /= error_none .or. token%finished .or. token%escaped) return
        minimum = 0_c_int64_t
        maximum = unlimited
        select case (token%character)
        case (42_c_int32_t)
            call next_token(parser, flags, token)
        case (43_c_int32_t)
            call next_token(parser, flags, token)
            minimum = 1_c_int64_t
        case (63_c_int32_t)
            call next_token(parser, flags, token)
            maximum = 1_c_int64_t
        case (123_c_int32_t)
            previous = parser%position
            call next_token(parser, flags, token)
            exists = read_bound(parser, minimum)
            if (parser%status /= error_none) return
            if (.not. exists) then
                parser%position = previous
                return
            end if
            if (raw_character(parser, 0_c_int64_t) == 125_c_int32_t) then
                maximum = minimum
            else if (raw_character(parser, 0_c_int64_t) == 44_c_int32_t) then
                parser%position = parser%position + 1_c_int64_t
                exists = read_bound(parser, maximum)
                if (parser%status /= error_none) return
                if (.not. exists) maximum = unlimited
            else
                parser%position = previous
                return
            end if
            if (raw_character(parser, 0_c_int64_t) /= 125_c_int32_t) then
                parser%position = previous
                return
            end if
            parser%position = parser%position + 1_c_int64_t
            if (minimum > maximum) then
                call set_error(parser, error_repeat, token%position)
                return
            end if
        case default
            return
        end select
        index = add_node(parser, node_repeat, flags)
        if (index == 0_c_int32_t) return
        parser%engine%nodes(index)%minimum = minimum
        parser%engine%nodes(index)%maximum = maximum
        call add_child(parser, index, child)
        call peek_token(parser, flags, token)
        if (parser%status /= error_none .or. token%finished .or. token%escaped) return
        if (token%character == 63_c_int32_t .or. token%character == 43_c_int32_t) then
            call next_token(parser, flags, token)
            parser%engine%nodes(index)%lazy = token%character == 63_c_int32_t
            parser%engine%nodes(index)%possessive = token%character == 43_c_int32_t
        end if
    end function parse_repeat

    integer(c_int32_t) function emit(engine, opcode, first, second, flags, character, status) result(index)
        type(engine_state), intent(inout) :: engine
        integer(c_int32_t), intent(in) :: opcode, first, second, flags, character
        integer(c_int), intent(inout) :: status
        type(instruction_type), allocatable :: expanded(:)
        integer :: count, allocation
        index = 0_c_int32_t
        if (status /= error_none) return
        count = 0
        if (allocated(engine%instructions)) count = size(engine%instructions)
        if (int(count, c_int64_t) >= int(huge(0_c_int32_t), c_int64_t)) then
            status = error_overflow
            return
        end if
        allocate(expanded(count + 1), stat=allocation)
        if (allocation /= 0) then
            status = error_memory
            return
        end if
        if (count /= 0) expanded(:count) = engine%instructions
        expanded(count + 1) = instruction_type(opcode, first, second, flags, character)
        call move_alloc(expanded, engine%instructions)
        index = int(count + 1, c_int32_t)
    end function emit

    integer(c_int32_t) function next_instruction(engine) result(index)
        type(engine_state), intent(in) :: engine
        integer :: count
        count = 0
        if (allocated(engine%instructions)) count = size(engine%instructions)
        index = int(count + 1, c_int32_t)
    end function next_instruction

    integer(c_int32_t) function add_repeat(engine, minimum, maximum, lazy, status) result(index)
        type(engine_state), intent(inout) :: engine
        integer(c_int64_t), intent(in) :: minimum, maximum
        logical, intent(in) :: lazy
        integer(c_int), intent(inout) :: status
        type(repeat_type), allocatable :: expanded(:)
        integer :: count, allocation
        index = 0_c_int32_t
        if (status /= error_none) return
        count = 0
        if (allocated(engine%repeats)) count = size(engine%repeats)
        allocate(expanded(count + 1), stat=allocation)
        if (allocation /= 0) then
            status = error_memory
            return
        end if
        if (count /= 0) expanded(:count) = engine%repeats
        expanded(count + 1) = repeat_type(minimum, maximum, lazy)
        call move_alloc(expanded, engine%repeats)
        index = int(count + 1, c_int32_t)
    end function add_repeat

    recursive subroutine compile_node(engine, node, status)
        type(engine_state), intent(inout) :: engine
        integer(c_int32_t), intent(in) :: node
        integer(c_int), intent(inout) :: status
        type(syntax_node) :: current
        integer(c_int32_t) :: location, branch, jump, repeat_id
        integer(c_int32_t), allocatable :: exits(:)
        integer :: child
        if (status /= error_none .or. node <= 0_c_int32_t) return
        current = engine%nodes(node)
        select case (current%kind)
        case (node_empty)
            return
        case (node_character)
            location = emit(engine, op_character, 0_c_int32_t, 0_c_int32_t, &
                current%flags, current%value, status)
        case (node_any)
            location = emit(engine, op_any, 0_c_int32_t, 0_c_int32_t, &
                current%flags, 0_c_int32_t, status)
        case (node_class)
            location = emit(engine, op_class, current%value, 0_c_int32_t, &
                current%flags, 0_c_int32_t, status)
        case (node_begin)
            location = emit(engine, op_begin, 0_c_int32_t, 0_c_int32_t, &
                current%flags, 0_c_int32_t, status)
        case (node_end)
            location = emit(engine, op_end, 0_c_int32_t, 0_c_int32_t, &
                current%flags, 0_c_int32_t, status)
        case (node_absolute_begin)
            location = emit(engine, op_absolute_begin, 0_c_int32_t, &
                0_c_int32_t, 0_c_int32_t, 0_c_int32_t, status)
        case (node_absolute_end)
            location = emit(engine, op_absolute_end, 0_c_int32_t, &
                0_c_int32_t, 0_c_int32_t, 0_c_int32_t, status)
        case (node_boundary)
            location = emit(engine, op_boundary, 0_c_int32_t, 0_c_int32_t, &
                current%flags, 0_c_int32_t, status)
        case (node_not_boundary)
            location = emit(engine, op_not_boundary, 0_c_int32_t, 0_c_int32_t, &
                current%flags, 0_c_int32_t, status)
        case (node_sequence)
            if (allocated(current%children)) then
                do child = 1, size(current%children)
                    call compile_node(engine, current%children(child), status)
                    if (status /= error_none) return
                end do
            end if
        case (node_alternation)
            if (.not. allocated(current%children)) return
            do child = 1, size(current%children) - 1
                branch = emit(engine, op_branch, 0_c_int32_t, 0_c_int32_t, &
                    0_c_int32_t, 0_c_int32_t, status)
                if (status /= error_none) return
                engine%instructions(branch)%first = next_instruction(engine)
                call compile_node(engine, current%children(child), status)
                jump = emit(engine, op_jump, 0_c_int32_t, 0_c_int32_t, &
                    0_c_int32_t, 0_c_int32_t, status)
                call add_integer(exits, jump, status)
                if (status /= error_none) return
                engine%instructions(branch)%second = next_instruction(engine)
            end do
            call compile_node(engine, current%children(size(current%children)), status)
            if (allocated(exits)) then
                do child = 1, size(exits)
                    engine%instructions(exits(child))%first = next_instruction(engine)
                end do
            end if
        case (node_capture)
            location = emit(engine, op_capture, current%value * 2_c_int32_t, &
                0_c_int32_t, 0_c_int32_t, 0_c_int32_t, status)
            call compile_node(engine, current%children(1), status)
            location = emit(engine, op_capture, current%value * 2_c_int32_t + &
                1_c_int32_t, 0_c_int32_t, 0_c_int32_t, 0_c_int32_t, status)
        case (node_reference)
            location = emit(engine, op_reference, current%value, 0_c_int32_t, &
                current%flags, 0_c_int32_t, status)
        case (node_repeat)
            if (current%possessive) then
                location = emit(engine, op_atomic_enter, 0_c_int32_t, 0_c_int32_t, &
                    0_c_int32_t, 0_c_int32_t, status)
            end if
            repeat_id = add_repeat(engine, current%minimum, current%maximum, &
                current%lazy, status)
            branch = emit(engine, op_repeat_enter, repeat_id, 0_c_int32_t, &
                0_c_int32_t, 0_c_int32_t, status)
            call compile_node(engine, current%children(1), status)
            location = emit(engine, op_repeat_again, repeat_id, branch, &
                0_c_int32_t, 0_c_int32_t, status)
            if (status /= error_none) return
            engine%instructions(branch)%second = next_instruction(engine)
            if (current%possessive) then
                location = emit(engine, op_atomic_leave, 0_c_int32_t, 0_c_int32_t, &
                    0_c_int32_t, 0_c_int32_t, status)
            end if
        case (node_atomic)
            location = emit(engine, op_atomic_enter, 0_c_int32_t, 0_c_int32_t, &
                0_c_int32_t, 0_c_int32_t, status)
            call compile_node(engine, current%children(1), status)
            location = emit(engine, op_atomic_leave, 0_c_int32_t, 0_c_int32_t, &
                0_c_int32_t, 0_c_int32_t, status)
        case default
            status = error_unsupported
        end select
    end subroutine compile_node

    logical function category_match(kind, bits, flags, byte_mode, character) result(matched)
        integer(c_int32_t), intent(in) :: kind, flags, character
        integer(c_int8_t), intent(in) :: bits
        logical, intent(in) :: byte_mode
        integer(c_int8_t) :: mask
        logical :: positive, ascii
        ascii = byte_mode .or. iand(flags, flag_ascii) /= 0_c_int32_t
        select case (kind)
        case (category_digit, category_not_digit)
            mask = merge(trait_ascii_digit, trait_unicode_digit, ascii)
            positive = kind == category_digit
        case (category_space, category_not_space)
            mask = merge(trait_ascii_space, trait_unicode_space, ascii)
            positive = kind == category_space
        case (category_word, category_not_word)
            if (byte_mode .and. iand(flags, flag_locale) /= 0_c_int32_t) then
                positive = kind == category_word
                matched = (rebar_fortran_locale_is_word(character) /= &
                    0_c_int32_t) .eqv. positive
                return
            else
                mask = merge(trait_ascii_word, trait_unicode_word, ascii)
            end if
            positive = kind == category_word
        case default
            matched = .false.
            return
        end select
        matched = (iand(bits, mask) /= 0_c_int8_t) .eqv. positive
    end function category_match

    pure integer(c_int32_t) function ascii_fold(character) result(folded)
        integer(c_int32_t), intent(in) :: character
        folded = character
        if (character >= 65_c_int32_t .and. character <= 90_c_int32_t) then
            folded = character + 32_c_int32_t
        end if
    end function ascii_fold

    logical function character_equal(engine, expected, actual, lower, flags) result(equal)
        type(engine_state), intent(in) :: engine
        integer(c_int32_t), intent(in) :: expected, actual, lower, flags
        equal = expected == actual
        if (equal .or. iand(flags, flag_ignorecase) == 0_c_int32_t) return
        if (engine%bytes .and. iand(flags, flag_locale) /= 0_c_int32_t) then
            equal = rebar_fortran_locale_case_key(expected) == &
                rebar_fortran_locale_case_key(actual)
            return
        end if
        if (engine%bytes .or. iand(flags, flag_ascii) /= 0_c_int32_t) then
            equal = ascii_fold(expected) == ascii_fold(actual)
            return
        end if
        equal = rebar_fortran_unicode_case_key(expected) == lower
    end function character_equal

    logical function range_case_equal(engine, first, last, character, lower, &
        flags) result(equal)
        type(engine_state), intent(in) :: engine
        integer(c_int32_t), intent(in) :: first, last, character, lower, flags
        integer(c_int32_t) :: candidate, folded, uppercase

        equal = .false.
        if (iand(flags, flag_ignorecase) == 0_c_int32_t) return
        if (engine%bytes .and. iand(flags, flag_locale) /= 0_c_int32_t) then
            folded = rebar_fortran_locale_case_key(character)
            do candidate = first, last
                if (rebar_fortran_locale_case_key(candidate) == folded) then
                    equal = .true.
                    return
                end if
            end do
            return
        end if

        if (engine%bytes .or. iand(flags, flag_ascii) /= 0_c_int32_t) then
            folded = ascii_fold(character)
            if (folded >= first .and. folded <= last) then
                equal = .true.
                return
            end if
            if (folded >= 97_c_int32_t .and. folded <= 122_c_int32_t) then
                uppercase = folded - 32_c_int32_t
                equal = uppercase >= first .and. uppercase <= last
            end if
            return
        end if

        if (lower >= first .and. lower <= last) then
            equal = .true.
            return
        end if
        do candidate = first, last
            if (rebar_fortran_unicode_case_key(candidate) == lower) then
                equal = .true.
                return
            end if
        end do
    end function range_case_equal

    logical function in_class(engine, index, character, lower, bits, flags) result(found)
        type(engine_state), intent(in) :: engine
        integer(c_int32_t), intent(in) :: index, character, lower, flags
        integer(c_int8_t), intent(in) :: bits
        integer :: item
        found = .false.
        if (.not. allocated(engine%classes)) return
        if (index <= 0_c_int32_t .or. index > size(engine%classes)) return
        if (allocated(engine%classes(index)%first)) then
            do item = 1, size(engine%classes(index)%first)
                if (character >= engine%classes(index)%first(item) .and. &
                    character <= engine%classes(index)%last(item)) then
                    found = .true.
                    exit
                end if
                if (range_case_equal(engine, &
                    engine%classes(index)%first(item), &
                    engine%classes(index)%last(item), &
                    character, lower, flags)) then
                    found = .true.
                    exit
                end if
            end do
        end if
        if (.not. found .and. allocated(engine%classes(index)%categories)) then
            do item = 1, size(engine%classes(index)%categories)
                if (category_match(engine%classes(index)%categories(item), &
                    bits, flags, engine%bytes, character)) then
                    found = .true.
                    exit
                end if
            end do
        end if
        if (engine%classes(index)%complemented) found = .not. found
    end function in_class

    subroutine push_state(stack, current, status)
        type(execution_state), allocatable, intent(inout) :: stack(:)
        type(execution_state), intent(in) :: current
        integer(c_int), intent(inout) :: status
        type(execution_state), allocatable :: expanded(:)
        integer :: count, allocation
        count = 0
        if (allocated(stack)) count = size(stack)
        allocate(expanded(count + 1), stat=allocation)
        if (allocation /= 0) then
            status = error_memory
            return
        end if
        if (count /= 0) expanded(:count) = stack
        expanded(count + 1) = current
        call move_alloc(expanded, stack)
    end subroutine push_state

    subroutine pop_state(stack, current, available, status)
        type(execution_state), allocatable, intent(inout) :: stack(:)
        type(execution_state), intent(out) :: current
        logical, intent(out) :: available
        integer(c_int), intent(inout) :: status
        type(execution_state), allocatable :: reduced(:)
        integer :: count, allocation
        available = .false.
        if (.not. allocated(stack)) return
        count = size(stack)
        if (count == 0) return
        current = stack(count)
        available = .true.
        if (count == 1) then
            deallocate(stack)
            return
        end if
        allocate(reduced(count - 1), stat=allocation)
        if (allocation /= 0) then
            status = error_memory
            available = .false.
            return
        end if
        reduced = stack(:count - 1)
        call move_alloc(reduced, stack)
    end subroutine pop_state

    subroutine discard_alternatives(stack, keep, status)
        type(execution_state), allocatable, intent(inout) :: stack(:)
        integer(c_int32_t), intent(in) :: keep
        integer(c_int), intent(inout) :: status
        type(execution_state), allocatable :: reduced(:)
        integer :: count, allocation
        if (.not. allocated(stack)) return
        count = size(stack)
        if (keep >= count) return
        if (keep <= 0_c_int32_t) then
            deallocate(stack)
            return
        end if
        allocate(reduced(keep), stat=allocation)
        if (allocation /= 0) then
            status = error_memory
            return
        end if
        reduced = stack(:keep)
        call move_alloc(reduced, stack)
    end subroutine discard_alternatives

    subroutine initial_state(engine, start, current, status)
        type(engine_state), intent(in) :: engine
        integer(c_int64_t), intent(in) :: start
        type(execution_state), intent(out) :: current
        integer(c_int), intent(inout) :: status
        integer :: allocation, repeat_count
        current%pc = 1_c_int32_t
        current%position = start
        current%last_group = unmatched
        allocate(current%captures(2 * (int(engine%groups) + 1)), stat=allocation)
        if (allocation /= 0) then
            status = error_memory
            return
        end if
        current%captures = unmatched
        current%captures(1) = start
        repeat_count = 0
        if (allocated(engine%repeats)) repeat_count = size(engine%repeats)
        allocate(current%repeat_count(repeat_count), &
            current%repeat_position(repeat_count), &
            current%repeat_active(repeat_count), &
            current%repeat_stalled(repeat_count), stat=allocation)
        if (allocation /= 0) then
            status = error_memory
            return
        end if
        current%repeat_count = 0_c_int64_t
        current%repeat_position = unmatched
        current%repeat_active = .false.
        current%repeat_stalled = .false.
    end subroutine initial_state

    subroutine execute_once(engine, characters, lower, traits, finish, start, &
        full, nonempty, result, found, status)
        type(engine_state), intent(in) :: engine
        integer(c_int32_t), intent(in) :: characters(:), lower(:)
        integer(c_int8_t), intent(in) :: traits(:)
        integer(c_int64_t), intent(in) :: finish, start
        logical, intent(in) :: full, nonempty
        type(execution_state), intent(out) :: result
        logical, intent(out) :: found
        integer(c_int), intent(inout) :: status
        type(execution_state) :: state, choice
        type(execution_state), allocatable :: stack(:)
        type(instruction_type) :: op
        integer(c_int32_t) :: group, repeat_id, saved, barriers
        integer(c_int64_t) :: first, last, width, offset
        integer :: allocation, stack_size
        logical :: failed, available, can_leave, can_continue

        found = .false.
        if (start > finish) return
        call initial_state(engine, start, state, status)
        if (status /= error_none) return
        do
            if (state%pc <= 0_c_int32_t .or. &
                state%pc > size(engine%instructions)) then
                failed = .true.
            else
                op = engine%instructions(state%pc)
                failed = .false.
                select case (op%opcode)
                case (op_character)
                    if (state%position >= finish) then
                        failed = .true.
                    else if (.not. character_equal(engine, op%character, &
                        characters(int(state%position + 1_c_int64_t)), &
                        lower(int(state%position + 1_c_int64_t)), op%flags)) then
                        failed = .true.
                    else
                        state%position = state%position + 1_c_int64_t
                        state%pc = state%pc + 1_c_int32_t
                    end if
                case (op_any)
                    if (state%position >= finish) then
                        failed = .true.
                    else if (iand(op%flags, flag_dotall) == 0_c_int32_t .and. &
                        characters(int(state%position + 1_c_int64_t)) == 10_c_int32_t) then
                        failed = .true.
                    else
                        state%position = state%position + 1_c_int64_t
                        state%pc = state%pc + 1_c_int32_t
                    end if
                case (op_class)
                    if (state%position >= finish) then
                        failed = .true.
                    else if (.not. in_class(engine, op%first, &
                        characters(int(state%position + 1_c_int64_t)), &
                        lower(int(state%position + 1_c_int64_t)), &
                        traits(int(state%position + 1_c_int64_t)), op%flags)) then
                        failed = .true.
                    else
                        state%position = state%position + 1_c_int64_t
                        state%pc = state%pc + 1_c_int32_t
                    end if
                case (op_begin)
                    if (state%position == 0_c_int64_t) then
                        state%pc = state%pc + 1_c_int32_t
                    else if (iand(op%flags, flag_multiline) /= 0_c_int32_t) then
                        if (characters(int(state%position)) == 10_c_int32_t) then
                            state%pc = state%pc + 1_c_int32_t
                        else
                            failed = .true.
                        end if
                    else
                        failed = .true.
                    end if
                case (op_end)
                    if (state%position == finish) then
                        state%pc = state%pc + 1_c_int32_t
                    else if (characters(int(state%position + 1_c_int64_t)) == &
                        10_c_int32_t .and. &
                        (iand(op%flags, flag_multiline) /= 0_c_int32_t .or. &
                         state%position + 1_c_int64_t == finish)) then
                        state%pc = state%pc + 1_c_int32_t
                    else
                        failed = .true.
                    end if
                case (op_absolute_begin)
                    if (state%position == 0_c_int64_t) then
                        state%pc = state%pc + 1_c_int32_t
                    else
                        failed = .true.
                    end if
                case (op_absolute_end)
                    if (state%position == finish) then
                        state%pc = state%pc + 1_c_int32_t
                    else
                        failed = .true.
                    end if
                case (op_boundary, op_not_boundary)
                    can_leave = .false.
                    can_continue = .false.
                    if (state%position > 0_c_int64_t) then
                        can_leave = category_match(category_word, &
                            traits(int(state%position)), op%flags, engine%bytes, &
                            characters(int(state%position)))
                    end if
                    if (state%position < finish) then
                        can_continue = category_match(category_word, &
                            traits(int(state%position + 1_c_int64_t)), &
                            op%flags, engine%bytes, &
                            characters(int(state%position + 1_c_int64_t)))
                    end if
                    if ((can_leave .neqv. can_continue) .eqv. &
                        (op%opcode == op_boundary)) then
                        state%pc = state%pc + 1_c_int32_t
                    else
                        failed = .true.
                    end if
                case (op_jump)
                    state%pc = op%first
                case (op_branch)
                    choice = state
                    choice%pc = op%second
                    call push_state(stack, choice, status)
                    if (status /= error_none) return
                    state%pc = op%first
                case (op_capture)
                    saved = op%first + 1_c_int32_t
                    if (saved <= 0_c_int32_t .or. saved > size(state%captures)) then
                        failed = .true.
                    else
                        state%captures(saved) = state%position
                        if (iand(op%first, 1_c_int32_t) /= 0_c_int32_t .and. &
                            op%first > 1_c_int32_t) then
                            state%last_group = int(op%first / 2_c_int32_t, c_int64_t)
                        end if
                        state%pc = state%pc + 1_c_int32_t
                    end if
                case (op_reference)
                    group = op%first
                    if (group <= 0_c_int32_t .or. group > engine%groups) then
                        failed = .true.
                    else
                        first = state%captures(int(group) * 2 + 1)
                        last = state%captures(int(group) * 2 + 2)
                        if (first == unmatched .or. last == unmatched) then
                            failed = .true.
                        else
                            width = last - first
                            if (width > finish - state%position) then
                                failed = .true.
                            else
                                do offset = 0_c_int64_t, width - 1_c_int64_t
                                    if (.not. character_equal(engine, &
                                        characters(int(first + offset + 1_c_int64_t)), &
                                        characters(int(state%position + offset + 1_c_int64_t)), &
                                        lower(int(state%position + offset + 1_c_int64_t)), &
                                        op%flags)) then
                                        failed = .true.
                                        exit
                                    end if
                                end do
                                if (.not. failed) then
                                    state%position = state%position + width
                                    state%pc = state%pc + 1_c_int32_t
                                end if
                            end if
                        end if
                    end if
                case (op_repeat_enter)
                    repeat_id = op%first
                    if (repeat_id <= 0_c_int32_t .or. &
                        repeat_id > size(state%repeat_count)) then
                        failed = .true.
                    else
                        if (.not. state%repeat_active(repeat_id)) then
                            state%repeat_active(repeat_id) = .true.
                            state%repeat_count(repeat_id) = 0_c_int64_t
                            state%repeat_stalled(repeat_id) = .false.
                        end if
                        can_leave = state%repeat_count(repeat_id) >= &
                            engine%repeats(repeat_id)%minimum
                        can_continue = state%repeat_count(repeat_id) < &
                            engine%repeats(repeat_id)%maximum .and. &
                            (.not. state%repeat_stalled(repeat_id) .or. &
                            state%repeat_count(repeat_id) < &
                            engine%repeats(repeat_id)%minimum)
                        if (.not. can_leave .and. .not. can_continue) then
                            failed = .true.
                        else if (can_leave .and. can_continue) then
                            choice = state
                            if (engine%repeats(repeat_id)%lazy) then
                                choice%pc = state%pc + 1_c_int32_t
                                choice%repeat_position(repeat_id) = state%position
                                call push_state(stack, choice, status)
                                state%repeat_active(repeat_id) = .false.
                                state%pc = op%second
                            else
                                choice%repeat_active(repeat_id) = .false.
                                choice%pc = op%second
                                call push_state(stack, choice, status)
                                state%repeat_position(repeat_id) = state%position
                                state%pc = state%pc + 1_c_int32_t
                            end if
                            if (status /= error_none) return
                        else if (can_continue) then
                            state%repeat_position(repeat_id) = state%position
                            state%pc = state%pc + 1_c_int32_t
                        else
                            state%repeat_active(repeat_id) = .false.
                            state%pc = op%second
                        end if
                    end if
                case (op_repeat_again)
                    repeat_id = op%first
                    if (repeat_id <= 0_c_int32_t .or. &
                        repeat_id > size(state%repeat_count)) then
                        failed = .true.
                    else
                        state%repeat_stalled(repeat_id) = &
                            state%repeat_position(repeat_id) == state%position
                        state%repeat_count(repeat_id) = &
                            state%repeat_count(repeat_id) + 1_c_int64_t
                        state%pc = op%second
                    end if
                case (op_atomic_enter)
                    stack_size = 0
                    if (allocated(stack)) stack_size = size(stack)
                    call add_integer(state%barriers, &
                        int(stack_size, c_int32_t), status)
                    if (status /= error_none) return
                    state%pc = state%pc + 1_c_int32_t
                case (op_atomic_leave)
                    if (.not. allocated(state%barriers)) then
                        failed = .true.
                    else
                        barriers = int(size(state%barriers), c_int32_t)
                        call discard_alternatives(stack, &
                            state%barriers(barriers), status)
                        if (status /= error_none) return
                        if (barriers == 1_c_int32_t) then
                            deallocate(state%barriers)
                        else
                            block
                                integer(c_int32_t), allocatable :: shortened(:)
                                allocate(shortened(barriers - 1_c_int32_t), &
                                    stat=allocation)
                                if (allocation /= 0) then
                                    status = error_memory
                                    return
                                end if
                                shortened = state%barriers(:barriers - 1_c_int32_t)
                                call move_alloc(shortened, state%barriers)
                            end block
                        end if
                        state%pc = state%pc + 1_c_int32_t
                    end if
                case (op_accept)
                    if ((full .and. state%position /= finish) .or. &
                        (nonempty .and. state%position == start)) then
                        failed = .true.
                    else
                        state%captures(2) = state%position
                        result = state
                        found = .true.
                        return
                    end if
                case default
                    status = error_unsupported
                    return
                end select
            end if
            if (failed) then
                call pop_state(stack, state, available, status)
                if (status /= error_none .or. .not. available) return
            end if
        end do
    end subroutine execute_once

    function rebar_fortran_compile(raw, folded, traits, length, flags, byte_mode, &
        error_position, error_code) result(handle) bind(C, name="rebar_fortran_compile")
        type(c_ptr), value, intent(in) :: raw, folded, traits
        integer(c_size_t), value, intent(in) :: length
        integer(c_int32_t), value, intent(in) :: flags
        integer(c_int), value, intent(in) :: byte_mode
        integer(c_int64_t), intent(out) :: error_position
        integer(c_int), intent(out) :: error_code
        type(c_ptr) :: handle
        type(engine_state), pointer :: engine
        type(parser_state) :: parser
        integer(c_int32_t), pointer :: incoming(:), incoming_folded(:)
        integer(c_int8_t), pointer :: incoming_traits(:)
        integer(c_int32_t) :: root, accepted
        integer :: allocation, count

        handle = c_null_ptr
        error_position = unmatched
        error_code = error_none
        if (length > int(huge(0), c_size_t)) then
            error_code = error_overflow
            return
        end if
        count = int(length)
        if (.not. c_associated(raw) .or. .not. c_associated(folded) .or. &
            .not. c_associated(traits)) then
            error_code = error_memory
            return
        end if
        allocate(engine, stat=allocation)
        if (allocation /= 0) then
            error_code = error_memory
            return
        end if
        allocate(engine%pattern(count), engine%folded_pattern(count), &
            engine%pattern_traits(count), stat=allocation)
        if (allocation /= 0) then
            deallocate(engine)
            error_code = error_memory
            return
        end if
        call c_f_pointer(raw, incoming, [count])
        call c_f_pointer(folded, incoming_folded, [count])
        call c_f_pointer(traits, incoming_traits, [count])
        engine%pattern = incoming
        engine%folded_pattern = incoming_folded
        engine%pattern_traits = incoming_traits
        engine%flags = flags
        engine%bytes = byte_mode /= 0_c_int
        parser%engine => engine
        parser%length = int(count, c_int64_t)
        root = parse_alternation(parser, engine%flags)
        if (parser%status == error_none) then
            block
                type(token_type) :: remaining
                call next_token(parser, engine%flags, remaining)
                if (.not. remaining%finished .and. parser%status == error_none) then
                    call set_error(parser, error_parenthesis, remaining%position)
                end if
            end block
        end if
        if (parser%status == error_none) then
            call compile_node(engine, root, parser%status)
        end if
        if (parser%status == error_none) then
            accepted = emit(engine, op_accept, 0_c_int32_t, 0_c_int32_t, &
                0_c_int32_t, 0_c_int32_t, parser%status)
            if (accepted == 0_c_int32_t .and. parser%status == error_none) then
                parser%status = error_memory
            end if
        end if
        if (parser%status /= error_none) then
            error_position = parser%error_position
            error_code = parser%status
            deallocate(engine)
            return
        end if
        handle = c_loc(engine)
    end function rebar_fortran_compile

    subroutine rebar_fortran_destroy(handle) bind(C, name="rebar_fortran_destroy")
        type(c_ptr), value, intent(in) :: handle
        type(engine_state), pointer :: engine
        if (.not. c_associated(handle)) return
        call c_f_pointer(handle, engine)
        if (associated(engine)) deallocate(engine)
    end subroutine rebar_fortran_destroy

    integer(c_int32_t) function rebar_fortran_group_count(handle) &
        result(groups) bind(C, name="rebar_fortran_group_count")
        type(c_ptr), value, intent(in) :: handle
        type(engine_state), pointer :: engine
        groups = 0_c_int32_t
        if (.not. c_associated(handle)) return
        call c_f_pointer(handle, engine)
        if (associated(engine)) groups = engine%groups
    end function rebar_fortran_group_count

    integer(c_int32_t) function rebar_fortran_effective_flags(handle) &
        result(flags) bind(C, name="rebar_fortran_effective_flags")
        type(c_ptr), value, intent(in) :: handle
        type(engine_state), pointer :: engine
        flags = 0_c_int32_t
        if (.not. c_associated(handle)) return
        call c_f_pointer(handle, engine)
        if (associated(engine)) flags = engine%flags
    end function rebar_fortran_effective_flags

    integer(c_int32_t) function rebar_fortran_name_count(handle) &
        result(count) bind(C, name="rebar_fortran_name_count")
        type(c_ptr), value, intent(in) :: handle
        type(engine_state), pointer :: engine
        count = 0_c_int32_t
        if (.not. c_associated(handle)) return
        call c_f_pointer(handle, engine)
        if (associated(engine)) then
            if (allocated(engine%names)) count = int(size(engine%names), c_int32_t)
        end if
    end function rebar_fortran_name_count

    integer(c_int32_t) function rebar_fortran_name_length(handle, index) &
        result(length) bind(C, name="rebar_fortran_name_length")
        type(c_ptr), value, intent(in) :: handle
        integer(c_int32_t), value, intent(in) :: index
        type(engine_state), pointer :: engine
        length = -1_c_int32_t
        if (.not. c_associated(handle) .or. index < 0_c_int32_t) return
        call c_f_pointer(handle, engine)
        if (.not. associated(engine)) return
        if (.not. allocated(engine%names)) return
        if (index >= size(engine%names)) return
        length = int(size(engine%names(index + 1_c_int32_t)%characters), c_int32_t)
    end function rebar_fortran_name_length

    integer(c_int32_t) function rebar_fortran_name_group(handle, index) &
        result(number) bind(C, name="rebar_fortran_name_group")
        type(c_ptr), value, intent(in) :: handle
        integer(c_int32_t), value, intent(in) :: index
        type(engine_state), pointer :: engine
        number = -1_c_int32_t
        if (.not. c_associated(handle) .or. index < 0_c_int32_t) return
        call c_f_pointer(handle, engine)
        if (.not. associated(engine)) return
        if (.not. allocated(engine%names)) return
        if (index >= size(engine%names)) return
        number = engine%names(index + 1_c_int32_t)%number
    end function rebar_fortran_name_group

    integer(c_int) function rebar_fortran_copy_name(handle, index, destination, capacity) &
        result(status) bind(C, name="rebar_fortran_copy_name")
        type(c_ptr), value, intent(in) :: handle, destination
        integer(c_int32_t), value, intent(in) :: index
        integer(c_size_t), value, intent(in) :: capacity
        type(engine_state), pointer :: engine
        integer(c_int32_t), pointer :: output(:)
        integer :: count
        status = -1_c_int
        if (.not. c_associated(handle) .or. .not. c_associated(destination)) return
        if (index < 0_c_int32_t .or. capacity > int(huge(0), c_size_t)) return
        call c_f_pointer(handle, engine)
        if (.not. associated(engine)) return
        if (.not. allocated(engine%names)) return
        if (index >= size(engine%names)) return
        count = size(engine%names(index + 1_c_int32_t)%characters)
        if (int(count, c_size_t) > capacity) return
        call c_f_pointer(destination, output, [int(capacity)])
        if (count /= 0) output(:count) = engine%names(index + 1_c_int32_t)%characters
        status = 0_c_int
    end function rebar_fortran_copy_name

    integer(c_int) function rebar_fortran_execute(handle, raw, folded, traits, &
        length, start, finish, mode, nonempty, captures, capacity, last_group) &
        result(outcome) bind(C, name="rebar_fortran_execute")
        type(c_ptr), value, intent(in) :: handle, raw, folded, traits, captures
        integer(c_size_t), value, intent(in) :: length, capacity
        integer(c_int64_t), value, intent(in) :: start, finish
        integer(c_int), value, intent(in) :: mode, nonempty
        integer(c_int64_t), intent(out) :: last_group
        type(engine_state), pointer :: engine
        integer(c_int32_t), pointer :: characters(:), lowered(:)
        integer(c_int8_t), pointer :: categories(:)
        integer(c_int64_t), pointer :: output(:)
        type(execution_state) :: result_state
        integer(c_int64_t) :: position, last
        integer(c_int) :: status
        logical :: found

        outcome = -1_c_int
        last_group = unmatched
        if (.not. c_associated(handle) .or. .not. c_associated(raw) .or. &
            .not. c_associated(folded) .or. .not. c_associated(traits) .or. &
            .not. c_associated(captures)) return
        if (length > int(huge(0), c_size_t) .or. &
            capacity > int(huge(0), c_size_t)) return
        if (start < 0_c_int64_t .or. finish < 0_c_int64_t) return
        if (int(finish, c_size_t) > length) return
        call c_f_pointer(handle, engine)
        if (.not. associated(engine)) return
        if (capacity < int(2_c_int64_t * &
            (int(engine%groups, c_int64_t) + 1_c_int64_t), c_size_t)) return
        call c_f_pointer(raw, characters, [int(length)])
        call c_f_pointer(folded, lowered, [int(length)])
        call c_f_pointer(traits, categories, [int(length)])
        call c_f_pointer(captures, output, [int(capacity)])
        output = unmatched
        if (start > finish) then
            outcome = 0_c_int
            return
        end if
        if (mode < 0_c_int .or. mode > 2_c_int) return
        last = finish
        status = error_none
        do position = start, last
            call execute_once(engine, characters, lowered, categories, finish, &
                position, mode == 2_c_int, &
                nonempty /= 0_c_int .and. position == start, &
                result_state, found, status)
            if (status /= error_none) return
            if (found) then
                output(:size(result_state%captures)) = result_state%captures
                last_group = result_state%last_group
                outcome = 1_c_int
                return
            end if
            if (mode /= 0_c_int) exit
        end do
        outcome = 0_c_int
    end function rebar_fortran_execute

end module rebar_fortran_engine
