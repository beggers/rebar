#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum { OP_CHAR=1, OP_DOT, OP_CAT, OP_CLASS, OP_ANCHOR, OP_BOUNDARY, OP_BACKREF,
       OP_SAVE_START, OP_SAVE_END, OP_SPLIT, OP_JUMP, OP_LOOK, OP_ATOMIC_START,
       OP_ATOMIC_END, OP_COND, OP_MATCH, OP_REPEAT1 };
enum { F_I=2, F_L=4, F_M=8, F_S=16, F_A=256 };
#define F_BYTE ((Py_ssize_t)1 << 31)

typedef struct { int op; Py_ssize_t a, b, c; } Ins;
typedef struct { Py_ssize_t count, atomic_capacity, suffix_width; int linear, compact, has_suffix, has_loop, split_disjoint; Ins *ins; PyObject *literal; } Code;
typedef struct { int kind; Py_UCS4 a, b; } ClassItem;
typedef struct { Py_ssize_t count; ClassItem *items; unsigned char ascii[256], ignore_ascii[256], ignore_unicode[256]; int ready; } CharClass;
typedef struct { Py_ssize_t code_count, class_count, groups; Code *codes; CharClass *classes; PyObject *literal; unsigned char starts[256]; uint64_t *start_pairs; uint32_t start_triples[128]; int starts_ready, cache_classes, triple_count; } VM;
typedef struct { PyObject *obj; int byte_mode, unicode_kind; Py_ssize_t length; const char *bytes; const void *unicode_data; } Subject;
typedef struct { Py_ssize_t pc, pos, last, repeat_step, repeat_limit; Py_ssize_t *caps, *seen, *barrier; int atomic_depth; } State;
typedef struct { State **items; Py_ssize_t length, capacity; } Stack;

enum { PROFILE_FIND, PROFILE_START, PROFILE_START_REJECT, PROFILE_PAIR_REJECT, PROFILE_EXECUTE,
       PROFILE_LINEAR, PROFILE_COMPACT, PROFILE_GENERAL, PROFILE_STATE_NEW, PROFILE_STATE_CLONE,
       PROFILE_LOOK, PROFILE_CLASS, PROFILE_REPEAT, PROFILE_STEP, PROFILE_COUNT };
#ifdef REBAR_VM_PROFILE
static uint64_t profile_counts[PROFILE_COUNT];
#define PROFILE_ADD(index, value) (profile_counts[(index)] += (uint64_t)(value))
#else
#define PROFILE_ADD(index, value) ((void)0)
#endif

static void state_free(State *s) {
    if (!s) return;
    PyMem_Free(s);
}

static State *state_new(Py_ssize_t groups, const Code *code, Py_ssize_t pos,
                        const Py_ssize_t *caps, Py_ssize_t last) {
    Py_ssize_t cap_count = 2 * (groups + 1);
    State *s = PyMem_Malloc(sizeof(State) + (size_t)(cap_count + code->count + code->atomic_capacity) * sizeof(Py_ssize_t));
    PROFILE_ADD(PROFILE_STATE_NEW,1);
    if (!s) return NULL;
    s->caps = (Py_ssize_t *)(s + 1);
    s->seen = s->caps + cap_count;
    s->barrier = s->seen + code->count;
    memcpy(s->caps, caps, (size_t)cap_count * sizeof(Py_ssize_t));
    for (Py_ssize_t i=0; i<code->count; i++) s->seen[i] = -1;
    s->pos = pos;
    s->pc = 0;
    s->last = last;
    s->repeat_step = 0;
    s->repeat_limit = 0;
    s->atomic_depth = 0;
    return s;
}

static State *state_clone(const State *old, Py_ssize_t groups, const Code *code) {
    Py_ssize_t cap_count = 2 * (groups + 1);
    State *s = PyMem_Malloc(sizeof(State) + (size_t)(cap_count + code->count + code->atomic_capacity) * sizeof(Py_ssize_t));
    PROFILE_ADD(PROFILE_STATE_CLONE,1);
    if (!s) return NULL;
    s->pc = old->pc;
    s->pos = old->pos;
    s->last = old->last;
    s->repeat_step = old->repeat_step;
    s->repeat_limit = old->repeat_limit;
    s->atomic_depth = old->atomic_depth;
    s->caps = (Py_ssize_t *)(s + 1);
    s->seen = s->caps + cap_count;
    s->barrier = s->seen + code->count;
    memcpy(s->caps, old->caps, (size_t)(cap_count + code->count) * sizeof(Py_ssize_t));
    if (s->atomic_depth) memcpy(s->barrier, old->barrier, (size_t)s->atomic_depth * sizeof(Py_ssize_t));
    return s;
}

static int stack_push(Stack *stack, State *s) {
    if (stack->length == stack->capacity) {
        Py_ssize_t next = stack->capacity ? stack->capacity * 2 : 32;
        State **items = PyMem_Realloc(stack->items, (size_t)next * sizeof(State *));
        if (!items) return 0;
        stack->items = items;
        stack->capacity = next;
    }
    stack->items[stack->length++] = s;
    return 1;
}

static State *stack_pop(Stack *stack) {
    return stack->length ? stack->items[--stack->length] : NULL;
}

static void stack_trim(Stack *stack, Py_ssize_t length) {
    while (stack->length > length) state_free(stack->items[--stack->length]);
}

static Py_UCS4 subject_char(const Subject *s, Py_ssize_t pos) {
    if (s->byte_mode) return (unsigned char)s->bytes[pos];
    return PyUnicode_READ(s->unicode_kind,s->unicode_data,pos);
}

static Py_UCS4 folded(Py_UCS4 c, int ascii_only) {
    if (ascii_only) return c < 128 ? (c >= 'A' && c <= 'Z' ? c + 32 : c) : c;
    if (c == 0x130 || c == 0x131) return 'i';
    if (c == 0x17f) return 's';
    if (c == 0x212a) return 'k';
    if (c == 0x1c80) return 0x432;
    if (c == 0xfb05 || c == 0xfb06) return 0xfb05;
    if (c == 0xdf || c == 0x1e9e) return 0xdf;
    return Py_UNICODE_TOLOWER(c);
}

static int range_case_match(Py_UCS4 left, Py_UCS4 right, Py_UCS4 value, int ascii_only) {
    if (value>=left && value<=right) return 1;
    if (ascii_only) {
        Py_UCS4 lower=value<128 && value>='A' && value<='Z' ? value+32 : value;
        Py_UCS4 upper=value<128 && value>='a' && value<='z' ? value-32 : value;
        return (lower>=left && lower<=right) || (upper>=left && upper<=right);
    }
    Py_UCS4 lower=Py_UNICODE_TOLOWER(value),upper=Py_UNICODE_TOUPPER(value),fold=folded(value,0);
    if ((lower>=left && lower<=right) || (upper>=left && upper<=right) || (fold>=left && fold<=right)) return 1;
    if ((value==0x412 || value==0x432 || value==0x1c80) && ((0x412>=left && 0x412<=right) || (0x432>=left && 0x432<=right) || (0x1c80>=left && 0x1c80<=right))) return 1;
    if ((value=='I' || value=='i' || value==0x130 || value==0x131) && (('I'>=left && 'I'<=right) || ('i'>=left && 'i'<=right) || (0x130>=left && 0x130<=right) || (0x131>=left && 0x131<=right))) return 1;
    if ((value=='S' || value=='s' || value==0x17f) && (('S'>=left && 'S'<=right) || ('s'>=left && 's'<=right) || (0x17f>=left && 0x17f<=right))) return 1;
    if ((value=='K' || value=='k' || value==0x212a) && (('K'>=left && 'K'<=right) || ('k'>=left && 'k'<=right) || (0x212a>=left && 0x212a<=right))) return 1;
    if ((value==0xfb05 || value==0xfb06) && ((0xfb05>=left && 0xfb05<=right) || (0xfb06>=left && 0xfb06<=right))) return 1;
    if ((value==0xdf || value==0x1e9e) && ((0xdf>=left && 0xdf<=right) || (0x1e9e>=left && 0x1e9e<=right))) return 1;
    return 0;
}

static int equal_char(Py_UCS4 a, Py_UCS4 b, Py_ssize_t flags) {
    if (!(flags & F_I)) return a == b;
    int ascii_only = !!(flags & (F_A|F_L|F_BYTE));
    return folded(a, ascii_only) == folded(b, ascii_only);
}

static int category(Py_UCS4 c, Py_ssize_t code, Py_ssize_t flags) {
    int ascii_only = !!(flags & (F_A|F_L|F_BYTE));
    int value;
    Py_UCS4 lower = (Py_UCS4)(code >= 'A' && code <= 'Z' ? code + 32 : code);
    if (lower == 'd') value = ascii_only ? (c >= '0' && c <= '9') : Py_UNICODE_ISDECIMAL(c);
    else if (lower == 's') value = ascii_only ? (c==' '||c=='\t'||c=='\n'||c=='\r'||c=='\v'||c=='\f') : Py_UNICODE_ISSPACE(c);
    else value = ascii_only ? (c < 128 && ((c>='0'&&c<='9')||(c>='A'&&c<='Z')||(c>='a'&&c<='z')||c=='_')) : (Py_UNICODE_ISALNUM(c)||c=='_');
    return code >= 'A' && code <= 'Z' ? !value : value;
}

static int class_match_slow(const VM *vm, Py_ssize_t index, Py_UCS4 c, Py_ssize_t flags, int negate) {
    if (index < 0 || index >= vm->class_count) return 0;
    CharClass cls = vm->classes[index];
    int found = 0;
    int ascii_only = !!(flags & (F_A|F_L|F_BYTE));
    for (Py_ssize_t i=0; i<cls.count && !found; i++) {
        ClassItem item = cls.items[i];
        if (item.kind == 1) found = equal_char(item.a, c, flags);
        else if (item.kind == 2) {
            found = (flags & F_I) ? range_case_match(item.a,item.b,c,ascii_only) : (c>=item.a && c<=item.b);
        } else if (item.kind == 3) found = category(c, item.a, flags);
    }
    return negate ? !found : found;
}

static int class_match(const VM *vm, Py_ssize_t index, Py_UCS4 c, Py_ssize_t flags, int negate) {
    PROFILE_ADD(PROFILE_CLASS,1);
    if (index < 0 || index >= vm->class_count) return 0;
    if (c<256 && vm->cache_classes) {
        CharClass *cls=&vm->classes[index];
        int table=!(flags&F_I) ? 0 : (flags&(F_A|F_L|F_BYTE)) ? 1 : 2;
        unsigned char *values=table==0 ? cls->ascii : table==1 ? cls->ignore_ascii : cls->ignore_unicode;
        if (!(cls->ready&(1<<table))) {
            for (Py_UCS4 value=0; value<256; value++) {
                Py_ssize_t table_flags=table==0 ? 0 : table==1 ? F_I|F_A : F_I;
                values[value]=(unsigned char)class_match_slow(vm,index,value,table_flags,0);
            }
            cls->ready|=1<<table;
        }
        int found=values[c];
        return negate ? !found : found;
    }
    return class_match_slow(vm,index,c,flags,negate);
}

static int atom_match(const VM *vm, const Subject *subject, Py_ssize_t pos, Ins atom) {
    Py_UCS4 value=subject_char(subject,pos);
    if (atom.op==OP_CHAR) return equal_char(value,(Py_UCS4)atom.a,atom.b);
    if (atom.op==OP_DOT) return (atom.a & F_S) || value!='\n';
    if (atom.op==OP_CAT) return category(value,atom.a,atom.b);
    if (atom.op==OP_CLASS) return class_match(vm,atom.a,value,atom.b,(int)atom.c);
    return 0;
}

static int atom_accepts(const VM *vm, Ins atom, Py_UCS4 value) {
    if (atom.op==OP_CHAR) return equal_char(value,(Py_UCS4)atom.a,atom.b);
    if (atom.op==OP_DOT) return (atom.a & F_S) || value!='\n';
    if (atom.op==OP_CAT) return category(value,atom.a,atom.b);
    if (atom.op==OP_CLASS) return class_match(vm,atom.a,value,atom.b,(int)atom.c);
    return 0;
}

static Py_ssize_t atom_run(const VM *vm, const Subject *subject, Py_ssize_t pos, Py_ssize_t maximum, Ins atom) {
    if (maximum<=0) return 0;
    if (atom.op==OP_DOT) {
        if (atom.a&F_S) return maximum;
        if (subject->byte_mode || subject->unicode_kind==PyUnicode_1BYTE_KIND) {
            const unsigned char *data=subject->byte_mode ? (const unsigned char *)subject->bytes : (const unsigned char *)subject->unicode_data;
            const unsigned char *newline=memchr(data+pos,'\n',(size_t)maximum);
            return newline ? (Py_ssize_t)(newline-(data+pos)) : maximum;
        }
    }
    if (atom.op==OP_CHAR && !(atom.b&F_I)) {
        Py_UCS4 wanted=(Py_UCS4)atom.a;
        Py_ssize_t matched=0;
        while (matched<maximum && subject_char(subject,pos+matched)==wanted) matched++;
        return matched;
    }
    if (atom.op==OP_CLASS && atom.a>=0 && atom.a<vm->class_count && (subject->byte_mode || subject->unicode_kind==PyUnicode_1BYTE_KIND)) {
        CharClass *cls=&vm->classes[atom.a];
        int table=!(atom.b&F_I) ? 0 : (atom.b&(F_A|F_L|F_BYTE)) ? 1 : 2;
        if (!(cls->ready&(1<<table))) (void)class_match(vm,atom.a,0,atom.b,0);
        const unsigned char *values=table==0 ? cls->ascii : table==1 ? cls->ignore_ascii : cls->ignore_unicode;
        const unsigned char *data=subject->byte_mode ? (const unsigned char *)subject->bytes : (const unsigned char *)subject->unicode_data;
        Py_ssize_t matched=0;
        while (matched<maximum && (!!values[data[pos+matched]]!=!!atom.c)) matched++;
        return matched;
    }
    Py_ssize_t matched=0;
    while (matched<maximum && atom_match(vm,subject,pos+matched,atom)) matched++;
    return matched;
}

static int leading_accepts(const VM *vm, const Code *code, Py_ssize_t pc, Py_UCS4 value, int depth) {
    if (depth>128 || pc<0 || pc>=code->count) return 1;
    Ins in=code->ins[pc];
    if (in.op==OP_CHAR || in.op==OP_DOT || in.op==OP_CAT || in.op==OP_CLASS) return atom_accepts(vm,in,value);
    if (in.op==OP_REPEAT1) {
        if (pc+1>=code->count) return 1;
        int atom=atom_accepts(vm,code->ins[pc+1],value);
        return in.a>0 ? atom : (atom || leading_accepts(vm,code,pc+2,value,depth+1));
    }
    if (in.op==OP_SPLIT) return leading_accepts(vm,code,in.a,value,depth+1) || leading_accepts(vm,code,in.b,value,depth+1);
    if (in.op==OP_JUMP) return leading_accepts(vm,code,in.a,value,depth+1);
    if (in.op==OP_COND) return leading_accepts(vm,code,in.b,value,depth+1) || leading_accepts(vm,code,in.c,value,depth+1);
    if (in.op==OP_LOOK && (in.b&3)==1 && in.a>=0 && in.a<vm->code_count) {
        return leading_accepts(vm,&vm->codes[in.a],0,value,depth+1) && leading_accepts(vm,code,pc+1,value,depth+1);
    }
    if (in.op==OP_SAVE_START || in.op==OP_SAVE_END || in.op==OP_ANCHOR || in.op==OP_BOUNDARY || in.op==OP_LOOK || in.op==OP_ATOMIC_START || in.op==OP_ATOMIC_END) return leading_accepts(vm,code,pc+1,value,depth+1);
    return 1;
}

static int leading_pair_accepts(const VM *vm, const Code *code, Py_ssize_t pc, Py_UCS4 first, Py_UCS4 second, int consumed, int depth) {
    if (depth>128 || pc<0 || pc>=code->count || consumed>=2) return 1;
    Ins in=code->ins[pc];
    if (in.op==OP_CHAR || in.op==OP_DOT || in.op==OP_CAT || in.op==OP_CLASS) {
        if (!atom_accepts(vm,in,consumed ? second : first)) return 0;
        return leading_pair_accepts(vm,code,pc+1,first,second,consumed+1,depth+1);
    }
    if (in.op==OP_REPEAT1) {
        if (pc+1>=code->count) return 1;
        Ins atom=code->ins[pc+1];
        int need=2-consumed;
        Py_ssize_t minimum=in.a;
        if (minimum>need) minimum=need;
        for (Py_ssize_t index=0; index<minimum; index++) if (!atom_accepts(vm,atom,consumed+index ? second : first)) return 0;
        consumed+=(int)minimum;
        if (consumed>=2) return 1;
        if ((in.b<0 || in.b>minimum) && atom_accepts(vm,atom,consumed ? second : first)) return 1;
        return leading_pair_accepts(vm,code,pc+2,first,second,consumed,depth+1);
    }
    if (in.op==OP_SPLIT) return leading_pair_accepts(vm,code,in.a,first,second,consumed,depth+1) || leading_pair_accepts(vm,code,in.b,first,second,consumed,depth+1);
    if (in.op==OP_JUMP) return leading_pair_accepts(vm,code,in.a,first,second,consumed,depth+1);
    if (in.op==OP_COND) return leading_pair_accepts(vm,code,in.b,first,second,consumed,depth+1) || leading_pair_accepts(vm,code,in.c,first,second,consumed,depth+1);
    if (in.op==OP_SAVE_START || in.op==OP_SAVE_END || in.op==OP_ANCHOR || in.op==OP_BOUNDARY || in.op==OP_LOOK || in.op==OP_ATOMIC_START || in.op==OP_ATOMIC_END) return leading_pair_accepts(vm,code,pc+1,first,second,consumed,depth+1);
    return 1;
}

static int start_accepts(const VM *vm, Py_UCS4 value) {
    if (value>=256 || !vm->code_count || !vm->codes[0].count) return 1;
    VM *mutable=(VM *)vm;
    if (!mutable->starts_ready) {
        for (Py_UCS4 item=0; item<256; item++) mutable->starts[item]=(unsigned char)leading_accepts(vm,&vm->codes[0],0,item,0);
        Py_ssize_t pc=0;
        while (pc<vm->codes[0].count && (vm->codes[0].ins[pc].op==OP_SAVE_START || vm->codes[0].ins[pc].op==OP_ANCHOR || vm->codes[0].ins[pc].op==OP_BOUNDARY)) pc++;
        if (pc<vm->codes[0].count && vm->codes[0].ins[pc].op==OP_SPLIT) {
            mutable->start_pairs=PyMem_Calloc(1024,sizeof(uint64_t));
            if (mutable->start_pairs) {
                for (Py_UCS4 first=0; first<256; first++) if (mutable->starts[first]) {
                    for (Py_UCS4 second=0; second<256; second++) if (leading_pair_accepts(vm,&vm->codes[0],0,first,second,0,0)) {
                        Py_ssize_t bit=((Py_ssize_t)first<<8)|second;
                        mutable->start_pairs[bit>>6]|=(uint64_t)1<<(bit&63);
                    }
                }
            }
        }
        mutable->starts_ready=1;
    }
    return mutable->starts[value];
}

static int repeat_needs_choice_inner(const VM *vm, const Code *code, Py_ssize_t next_pc, Ins atom, int depth) {
    if (depth>32) return 1;
    while (next_pc<code->count && (code->ins[next_pc].op==OP_SAVE_START || code->ins[next_pc].op==OP_SAVE_END)) next_pc++;
    if (next_pc>=code->count || code->ins[next_pc].op==OP_MATCH) return 0;
    Ins next=code->ins[next_pc];
    if (next.op==OP_JUMP) return repeat_needs_choice_inner(vm,code,next.a,atom,depth+1);
    if (next.op==OP_SPLIT) return repeat_needs_choice_inner(vm,code,next.a,atom,depth+1) || repeat_needs_choice_inner(vm,code,next.b,atom,depth+1);
    if (next.op==OP_ANCHOR && (next.a=='$' || next.a=='Z')) {
        if (next.a=='$' && (next.b & F_M) && atom_accepts(vm,atom,'\n')) return 1;
        return 0;
    }
    if (next.op==OP_CHAR && !atom_accepts(vm,atom,(Py_UCS4)next.a)) return 0;
    if (next.op==OP_LOOK && (next.b & 1) && !(next.b & 2) && next.a>=0 && next.a<vm->code_count) {
        Code look=vm->codes[next.a];
        if (look.count && look.ins[0].op==OP_CHAR && !atom_accepts(vm,atom,(Py_UCS4)look.ins[0].a)) return 0;
    }
    return 1;
}

static int repeat_needs_choice(const VM *vm, const Code *code, Py_ssize_t next_pc, Ins atom) {
    return repeat_needs_choice_inner(vm,code,next_pc,atom,0);
}

static int execute_linear(const VM *vm, Py_ssize_t code_index, const Subject *subject,
                          Py_ssize_t start, Py_ssize_t endpos, Py_ssize_t *caps,
                          Py_ssize_t *last, Py_ssize_t *out_pos, int require_end,
                          int require_nonempty) {
    const Code *code=&vm->codes[code_index];
    PROFILE_ADD(PROFILE_LINEAR,1);
    Py_ssize_t pos=start;
    for (Py_ssize_t pc=0; pc<code->count; pc++) {
        PROFILE_ADD(PROFILE_STEP,1);
        Ins in=code->ins[pc];
        switch (in.op) {
            case OP_CHAR:
                if (pos>=endpos || !equal_char(subject_char(subject,pos),(Py_UCS4)in.a,in.b)) return 0;
                pos++; break;
            case OP_DOT:
                if (pos>=endpos || (!(in.a & F_S) && subject_char(subject,pos)=='\n')) return 0;
                pos++; break;
            case OP_CAT:
                if (pos>=endpos || !category(subject_char(subject,pos),in.a,in.b)) return 0;
                pos++; break;
            case OP_CLASS:
                if (pos>=endpos || !class_match(vm,in.a,subject_char(subject,pos),in.b,(int)in.c)) return 0;
                pos++; break;
            case OP_REPEAT1: {
                if (pc+1>=code->count || in.a<0 || (in.b>=0 && in.b<in.a) || in.c==1) return -2;
                Ins atom=code->ins[++pc];
                Py_ssize_t maximum=in.b<0 ? endpos-pos : in.b;
                if (maximum>endpos-pos) maximum=endpos-pos;
                Py_ssize_t matched=atom_run(vm,subject,pos,maximum,atom);
                PROFILE_ADD(PROFILE_REPEAT,matched);
                if (matched<in.a) return 0;
                pos+=matched; break;
            }
            case OP_ANCHOR: {
                int ok=0;
                if (in.a=='^') ok=pos==0 || ((in.b & F_M) && pos>0 && subject_char(subject,pos-1)=='\n');
                else if (in.a=='$') ok=pos==endpos || (pos+1==endpos && pos<subject->length && subject_char(subject,pos)=='\n') || ((in.b & F_M) && pos<endpos && subject_char(subject,pos)=='\n');
                else if (in.a=='A') ok=pos==0;
                else ok=pos==endpos;
                if (!ok) return 0;
                break;
            }
            case OP_BOUNDARY: {
                int left=pos>0 && category(subject_char(subject,pos-1),'w',in.b);
                int right=pos<endpos && category(subject_char(subject,pos),'w',in.b);
                if ((left != right) != !!in.a) return 0;
                break;
            }
            case OP_BACKREF: {
                Py_ssize_t begin=caps[2*in.a],finish=caps[2*in.a+1];
                if (begin<0 || finish<begin || pos+finish-begin>endpos) return 0;
                for (Py_ssize_t i=0; i<finish-begin; i++) if (!equal_char(subject_char(subject,begin+i),subject_char(subject,pos+i),in.b)) return 0;
                pos+=finish-begin; break;
            }
            case OP_SAVE_START:
                caps[2*in.a]=pos; break;
            case OP_SAVE_END:
                caps[2*in.a+1]=pos; *last=in.a; break;
            case OP_LOOK: {
                PROFILE_ADD(PROFILE_LOOK,1);
                if (in.a<0 || in.a>=vm->code_count || !vm->codes[in.a].linear) return -2;
                Py_ssize_t substart=pos;
                int behind=!!(in.b & 2),positive=!!(in.b & 1);
                if (behind) substart-=in.c;
                if (substart<0) { if (positive) return 0; break; }
                Py_ssize_t local_caps[34],cap_count=2*(vm->groups+1);
                Py_ssize_t *look_caps=cap_count<=34 ? local_caps : PyMem_Malloc((size_t)cap_count*sizeof(Py_ssize_t));
                if (!look_caps) return -1;
                memcpy(look_caps,caps,(size_t)cap_count*sizeof(Py_ssize_t));
                Py_ssize_t look_last=*last,look_end=-1,look_limit=behind ? pos : endpos;
                int got=execute_linear(vm,in.a,subject,substart,look_limit,look_caps,&look_last,&look_end,behind,0);
                if (got<0) { if (look_caps!=local_caps) PyMem_Free(look_caps); return got; }
                int matched=got && (!behind || look_end==pos);
                if (positive && matched) { memcpy(caps,look_caps,(size_t)cap_count*sizeof(Py_ssize_t)); *last=look_last; }
                if (look_caps!=local_caps) PyMem_Free(look_caps);
                if (matched!=positive) return 0;
                break;
            }
            case OP_MATCH:
                if ((require_end && pos!=endpos) || (require_nonempty && pos==start)) return 0;
                *out_pos=pos; return 1;
            default: return -2;
        }
    }
    return 0;
}

static int execute(const VM *vm, Py_ssize_t code_index, const Subject *subject,
                   Py_ssize_t start, Py_ssize_t endpos, Py_ssize_t *caps,
                   Py_ssize_t *last, Py_ssize_t *out_pos, int require_end,
                   int require_nonempty, int depth);

static int execute_compact_path(const VM *vm, const Code *code, const Subject *subject,
                                Py_ssize_t pc, Py_ssize_t pos, Py_ssize_t start,
                                Py_ssize_t endpos, Py_ssize_t *caps, Py_ssize_t *last,
                                Py_ssize_t *out_pos, int require_end,
                                int require_nonempty, int depth) {
    if (depth>128) return -2;
    Py_ssize_t cap_count=2*(vm->groups+1);
    PROFILE_ADD(PROFILE_COMPACT,1);
    while (pc>=0 && pc<code->count) {
        PROFILE_ADD(PROFILE_STEP,1);
        Ins in=code->ins[pc];
        switch (in.op) {
            case OP_CHAR:
            case OP_DOT:
            case OP_CAT:
            case OP_CLASS:
                if (pos>=endpos || !atom_match(vm,subject,pos,in)) return 0;
                pos++; pc++; break;
            case OP_ANCHOR: {
                int ok=0;
                if (in.a=='^') ok=pos==0 || ((in.b & F_M) && pos>0 && subject_char(subject,pos-1)=='\n');
                else if (in.a=='$') ok=pos==endpos || (pos+1==endpos && pos<subject->length && subject_char(subject,pos)=='\n') || ((in.b & F_M) && pos<endpos && subject_char(subject,pos)=='\n');
                else if (in.a=='A') ok=pos==0;
                else ok=pos==endpos;
                if (!ok) return 0;
                pc++; break;
            }
            case OP_BOUNDARY: {
                int left=pos>0 && category(subject_char(subject,pos-1),'w',in.b);
                int right=pos<endpos && category(subject_char(subject,pos),'w',in.b);
                if ((left != right) != !!in.a) return 0;
                pc++; break;
            }
            case OP_BACKREF: {
                Py_ssize_t begin=caps[2*in.a],finish=caps[2*in.a+1];
                if (begin<0 || finish<begin || pos+finish-begin>endpos) return 0;
                for (Py_ssize_t i=0; i<finish-begin; i++) if (!equal_char(subject_char(subject,begin+i),subject_char(subject,pos+i),in.b)) return 0;
                pos+=finish-begin; pc++; break;
            }
            case OP_SAVE_START:
                caps[2*in.a]=pos; pc++; break;
            case OP_SAVE_END:
                caps[2*in.a+1]=pos; *last=in.a; pc++; break;
            case OP_JUMP:
                pc=in.a; break;
            case OP_COND:
                pc=caps[2*in.a]>=0 ? in.b : in.c; break;
            case OP_SPLIT: {
                Py_ssize_t saved_caps[34],saved_last=*last,finish=-1;
                memcpy(saved_caps,caps,(size_t)cap_count*sizeof(Py_ssize_t));
                int got=execute_compact_path(vm,code,subject,in.a,pos,start,endpos,caps,last,&finish,require_end,require_nonempty,depth+1);
                if (got) { if (got>0) *out_pos=finish; return got; }
                memcpy(caps,saved_caps,(size_t)cap_count*sizeof(Py_ssize_t)); *last=saved_last;
                pc=in.b; break;
            }
            case OP_REPEAT1: {
                if (pc+1>=code->count || in.a<0 || (in.b>=0 && in.b<in.a)) return -2;
                Ins atom=code->ins[pc+1];
                Py_ssize_t maximum=in.b<0 ? endpos-pos : in.b;
                if (maximum>endpos-pos) maximum=endpos-pos;
                Py_ssize_t matched=atom_run(vm,subject,pos,maximum,atom);
                PROFILE_ADD(PROFILE_REPEAT,matched);
                if (matched<in.a) return 0;
                Py_ssize_t minimum_pos=pos+in.a,maximum_pos=pos+matched;
                pc+=2;
                if (in.c>=2 || (in.c==0 && !repeat_needs_choice(vm,code,pc,atom))) { pos=maximum_pos; break; }
                Py_ssize_t first=in.c==1 ? minimum_pos : maximum_pos,step=in.c==1 ? 1 : -1,last_pos=in.c==1 ? maximum_pos : minimum_pos;
                Py_ssize_t saved_caps[34],saved_last=*last;
                memcpy(saved_caps,caps,(size_t)cap_count*sizeof(Py_ssize_t));
                for (Py_ssize_t candidate=first;;candidate+=step) {
                    Py_ssize_t finish=-1;
                    int got=execute_compact_path(vm,code,subject,pc,candidate,start,endpos,caps,last,&finish,require_end,require_nonempty,depth+1);
                    if (got) { if (got>0) *out_pos=finish; return got; }
                    if (candidate==last_pos) return 0;
                    memcpy(caps,saved_caps,(size_t)cap_count*sizeof(Py_ssize_t)); *last=saved_last;
                }
            }
            case OP_LOOK: {
                PROFILE_ADD(PROFILE_LOOK,1);
                if (in.a<0 || in.a>=vm->code_count) return -2;
                int behind=!!(in.b & 2),positive=!!(in.b & 1);
                Py_ssize_t substart=behind ? pos-in.c : pos;
                if (substart<0) { if (positive) return 0; pc++; break; }
                Py_ssize_t look_caps[34],look_last=*last,look_end=-1,look_limit=behind ? pos : endpos;
                memcpy(look_caps,caps,(size_t)cap_count*sizeof(Py_ssize_t));
                int got=execute(vm,in.a,subject,substart,look_limit,look_caps,&look_last,&look_end,behind,0,depth+1);
                if (got<0) return got;
                int matched=got && (!behind || look_end==pos);
                if (positive && matched) { memcpy(caps,look_caps,(size_t)cap_count*sizeof(Py_ssize_t)); *last=look_last; }
                if (matched!=positive) return 0;
                pc++; break;
            }
            case OP_MATCH:
                if ((require_end && pos!=endpos) || (require_nonempty && pos==start)) return 0;
                *out_pos=pos; return 1;
            default: return -2;
        }
    }
    return 0;
}

static int consume_simple_range(const VM *vm, const Code *code, const Subject *subject,
                                Py_ssize_t begin, Py_ssize_t end, Py_ssize_t endpos,
                                Py_ssize_t *position) {
    Py_ssize_t pos=*position;
    for (Py_ssize_t pc=begin; pc<end; pc++) {
        Ins in=code->ins[pc];
        if (in.op==OP_CHAR || in.op==OP_DOT || in.op==OP_CAT || in.op==OP_CLASS) {
            if (pos>=endpos || !atom_match(vm,subject,pos,in)) return 0;
            pos++; continue;
        }
        if (in.op==OP_REPEAT1 && pc+1<end && in.c!=1 && (in.c>=2 || !repeat_needs_choice(vm,code,pc+2,code->ins[pc+1]))) {
            Ins atom=code->ins[++pc];
            Py_ssize_t maximum=in.b<0 ? endpos-pos : in.b;
            if (maximum>endpos-pos) maximum=endpos-pos;
            Py_ssize_t matched=atom_run(vm,subject,pos,maximum,atom);
            if (matched<in.a) return 0;
            pos+=matched; continue;
        }
        return -1;
    }
    *position=pos;
    return 1;
}

static int execute_simple_loop(const VM *vm, const Code *code, const Subject *subject,
                               Py_ssize_t start, Py_ssize_t endpos, Py_ssize_t *out_pos,
                               int require_end, int require_nonempty) {
    Py_ssize_t split=-1,close=-1;
    for (Py_ssize_t pc=0; pc<code->count; pc++) {
        Ins in=code->ins[pc];
        if (in.op==OP_SPLIT) {
            if (split>=0 || in.c<0) return -1;
            split=pc;
        }
        if (in.op==OP_JUMP) {
            if (close>=0 || split<0 || in.a!=split) return -1;
            close=pc;
        }
    }
    if (split<0 || close<0 || code->ins[split].a!=split+1 || code->ins[split].b!=close+1 || code->ins[code->count-1].op!=OP_MATCH) return -1;
    Py_ssize_t pos=start;
    int prefix=consume_simple_range(vm,code,subject,0,split,endpos,&pos);
    if (prefix<0) return -1;
    if (!prefix) return 0;
    for (;;) {
        Py_ssize_t next=pos;
        int body=consume_simple_range(vm,code,subject,split+1,close,endpos,&next);
        if (body<0) return -1;
        if (!body) break;
        if (next==pos) return -1;
        pos=next;
    }
    int suffix=consume_simple_range(vm,code,subject,close+1,code->count-1,endpos,&pos);
    if (suffix<0) return -1;
    if (!suffix) return 0;
    if ((require_end && pos!=endpos) || (require_nonempty && pos==start)) return 0;
    *out_pos=pos;
    return 1;
}

static int execute(const VM *vm, Py_ssize_t code_index, const Subject *subject,
                   Py_ssize_t start, Py_ssize_t endpos, Py_ssize_t *caps,
                   Py_ssize_t *last, Py_ssize_t *out_pos, int require_end,
                   int require_nonempty, int depth) {
    PROFILE_ADD(PROFILE_EXECUTE,1);
    if (depth > 128 || code_index < 0 || code_index >= vm->code_count) return -2;
    const Code *code = &vm->codes[code_index];
    if (code->linear) return execute_linear(vm,code_index,subject,start,endpos,caps,last,out_pos,require_end,require_nonempty);
    if (code->compact && code->has_loop && !vm->groups) {
        int got=execute_simple_loop(vm,code,subject,start,endpos,out_pos,require_end,require_nonempty);
        if (got>=0) return got;
    }
    if (code->compact && vm->groups<=16) {
        int got=execute_compact_path(vm,code,subject,0,start,start,endpos,caps,last,out_pos,require_end,require_nonempty,0);
        if (got!=-2) return got;
    }
    PROFILE_ADD(PROFILE_GENERAL,1);
    Stack stack = {0};
    State *current = state_new(vm->groups, code, start, caps, *last);
    if (!current) return -1;
    for (;;) {
        PROFILE_ADD(PROFILE_STEP,1);
        if (!current) { PyMem_Free(stack.items); return 0; }
        if (current->pc < 0 || current->pc >= code->count) goto fail;
        Ins in = code->ins[current->pc];
        switch (in.op) {
            case OP_CHAR:
                if (current->pos >= endpos || !equal_char(subject_char(subject,current->pos), (Py_UCS4)in.a, in.b)) goto fail;
                current->pos++; current->pc++; break;
            case OP_DOT:
                if (current->pos >= endpos || (!(in.a & F_S) && subject_char(subject,current->pos)=='\n')) goto fail;
                current->pos++; current->pc++; break;
            case OP_CAT:
                if (current->pos >= endpos || !category(subject_char(subject,current->pos), in.a, in.b)) goto fail;
                current->pos++; current->pc++; break;
            case OP_CLASS:
                if (current->pos >= endpos || !class_match(vm,in.a,subject_char(subject,current->pos),in.b,(int)in.c)) goto fail;
                current->pos++; current->pc++; break;
            case OP_ANCHOR: {
                int ok = 0;
                if (in.a == '^') ok = current->pos==0 || ((in.b & F_M) && current->pos>0 && subject_char(subject,current->pos-1)=='\n');
                else if (in.a == '$') ok = current->pos==endpos || (current->pos+1==endpos && current->pos<subject->length && subject_char(subject,current->pos)=='\n') || ((in.b & F_M) && current->pos<endpos && subject_char(subject,current->pos)=='\n');
                else if (in.a == 'A') ok = current->pos==0;
                else ok = current->pos==endpos;
                if (!ok) goto fail;
                current->pc++; break;
            }
            case OP_BOUNDARY: {
                int left = current->pos>0 && category(subject_char(subject,current->pos-1),'w',in.b);
                int right = current->pos<endpos && category(subject_char(subject,current->pos),'w',in.b);
                if ((left != right) != !!in.a) goto fail;
                current->pc++; break;
            }
            case OP_BACKREF: {
                Py_ssize_t begin = current->caps[2*in.a], finish = current->caps[2*in.a+1];
                if (begin < 0 || finish < begin || current->pos + finish-begin > endpos) goto fail;
                for (Py_ssize_t i=0; i<finish-begin; i++) if (!equal_char(subject_char(subject,begin+i),subject_char(subject,current->pos+i),in.b)) goto fail;
                current->pos += finish-begin; current->pc++; break;
            }
            case OP_SAVE_START:
                current->caps[2*in.a] = current->pos; current->pc++; break;
            case OP_SAVE_END:
                current->caps[2*in.a+1] = current->pos; current->last = in.a; current->pc++; break;
            case OP_JUMP:
                current->pc = in.a; break;
            case OP_SPLIT: {
                if (in.c >= 0 && current->seen[current->pc] == current->pos) { current->pc = in.c; break; }
                if (in.c >= 0) current->seen[current->pc] = current->pos;
                State *alternate = state_clone(current,vm->groups,code);
                if (!alternate) { state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return -1; }
                alternate->pc = in.b;
                if (!stack_push(&stack,alternate)) { state_free(alternate); state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return -1; }
                current->pc = in.a; break;
            }
            case OP_REPEAT1: {
                if (current->pc+1>=code->count || in.a<0 || (in.b>=0 && in.b<in.a)) goto fail;
                Ins atom=code->ins[current->pc+1];
                Py_ssize_t begin=current->pos,maximum=in.b<0 ? endpos-begin : in.b;
                if (maximum>endpos-begin) maximum=endpos-begin;
                Py_ssize_t matched=atom_run(vm,subject,begin,maximum,atom);
                PROFILE_ADD(PROFILE_REPEAT,matched);
                if (matched<in.a) goto fail;
                Py_ssize_t minimum=begin+in.a,furthest=begin+matched;
                current->pc+=2;
                if (in.c==1) current->pos=minimum;
                else current->pos=furthest;
                if (in.c<2 && furthest>minimum && (in.c==1 || repeat_needs_choice(vm,code,current->pc,atom))) {
                    State *alternate=state_clone(current,vm->groups,code);
                    if (!alternate) { state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return -1; }
                    alternate->repeat_step=in.c==1 ? 1 : -1;
                    alternate->repeat_limit=in.c==1 ? furthest : minimum;
                    alternate->pos=current->pos+alternate->repeat_step;
                    if (!stack_push(&stack,alternate)) { state_free(alternate); state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return -1; }
                }
                break;
            }
            case OP_ATOMIC_START:
                if (current->atomic_depth >= code->atomic_capacity) goto fail;
                current->barrier[current->atomic_depth++] = stack.length;
                current->pc++; break;
            case OP_ATOMIC_END:
                if (!current->atomic_depth) goto fail;
                stack_trim(&stack,current->barrier[--current->atomic_depth]);
                current->pc++; break;
            case OP_COND:
                current->pc = current->caps[2*in.a] >= 0 ? in.b : in.c; break;
            case OP_LOOK: {
                PROFILE_ADD(PROFILE_LOOK,1);
                Py_ssize_t substart = current->pos;
                int behind = !!(in.b & 2), positive = !!(in.b & 1);
                if (behind) substart -= in.c;
                if (substart < 0) { if (positive) goto fail; current->pc++; break; }
                Py_ssize_t *look_caps = PyMem_Malloc((size_t)(2*(vm->groups+1))*sizeof(Py_ssize_t));
                if (!look_caps) { state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return -1; }
                memcpy(look_caps,current->caps,(size_t)(2*(vm->groups+1))*sizeof(Py_ssize_t));
                Py_ssize_t look_last=current->last, look_end=-1;
                Py_ssize_t look_limit = behind ? current->pos : endpos;
                int got = execute(vm,in.a,subject,substart,look_limit,look_caps,&look_last,&look_end,behind,0,depth+1);
                if (got < 0) { PyMem_Free(look_caps); state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return got; }
                int matched = got && (!behind || look_end==current->pos);
                if (positive && matched) { memcpy(current->caps,look_caps,(size_t)(2*(vm->groups+1))*sizeof(Py_ssize_t)); current->last=look_last; }
                PyMem_Free(look_caps);
                if (matched != positive) goto fail;
                current->pc++; break;
            }
            case OP_MATCH:
                if ((require_end && current->pos!=endpos) || (require_nonempty && current->pos==start)) goto fail;
                memcpy(caps,current->caps,(size_t)(2*(vm->groups+1))*sizeof(Py_ssize_t));
                *last=current->last; *out_pos=current->pos;
                state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return 1;
            default: goto fail;
        }
        continue;
fail:
        state_free(current);
        current = stack_pop(&stack);
        if (current && current->repeat_step) {
            Py_ssize_t next_pos=current->pos+current->repeat_step;
            if ((current->repeat_step>0 && next_pos<=current->repeat_limit) || (current->repeat_step<0 && next_pos>=current->repeat_limit)) {
                State *alternate=state_clone(current,vm->groups,code);
                if (!alternate) { state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return -1; }
                alternate->pos=next_pos;
                if (!stack_push(&stack,alternate)) { state_free(alternate); state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return -1; }
            }
            current->repeat_step=0;
        }
    }
}

static void vm_free(VM *vm) {
    if (!vm) return;
    for (Py_ssize_t i=0; i<vm->code_count; i++) { PyMem_Free(vm->codes[i].ins); Py_XDECREF(vm->codes[i].literal); }
    for (Py_ssize_t i=0; i<vm->class_count; i++) PyMem_Free(vm->classes[i].items);
    Py_XDECREF(vm->literal); PyMem_Free(vm->start_pairs);
    PyMem_Free(vm->codes); PyMem_Free(vm->classes); PyMem_Free(vm);
}

static void capsule_free(PyObject *capsule) { vm_free(PyCapsule_GetPointer(capsule,"rebar.vm")); }

static PyObject *native_build(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *programs, *classes;
    Py_ssize_t groups;
    if (!PyArg_ParseTuple(args,"OOn",&programs,&classes,&groups)) return NULL;
    PyObject *pseq = PySequence_Fast(programs,"programs must be a sequence");
    PyObject *cseq = PySequence_Fast(classes,"classes must be a sequence");
    if (!pseq || !cseq) { Py_XDECREF(pseq); Py_XDECREF(cseq); return NULL; }
    VM *vm = PyMem_Calloc(1,sizeof(VM));
    if (!vm) { Py_DECREF(pseq); Py_DECREF(cseq); return PyErr_NoMemory(); }
    vm->groups=groups; vm->code_count=PySequence_Fast_GET_SIZE(pseq); vm->class_count=PySequence_Fast_GET_SIZE(cseq);
    vm->codes=PyMem_Calloc((size_t)vm->code_count,sizeof(Code)); vm->classes=PyMem_Calloc((size_t)vm->class_count,sizeof(CharClass));
    if (!vm->codes || (!vm->classes && vm->class_count)) { vm_free(vm); Py_DECREF(pseq); Py_DECREF(cseq); return PyErr_NoMemory(); }
    for (Py_ssize_t p=vm->code_count; p-->0;) {
        PyObject *seq = PySequence_Fast(PySequence_Fast_GET_ITEM(pseq,p),"program must be a sequence");
        if (!seq) goto error;
        vm->codes[p].count=PySequence_Fast_GET_SIZE(seq); vm->codes[p].ins=PyMem_Calloc((size_t)vm->codes[p].count,sizeof(Ins));
        if (!vm->codes[p].ins) { Py_DECREF(seq); PyErr_NoMemory(); goto error; }
        for (Py_ssize_t i=0; i<vm->codes[p].count; i++) {
            PyObject *row=PySequence_Fast_GET_ITEM(seq,i);
            if (!PyArg_ParseTuple(row,"innn",&vm->codes[p].ins[i].op,&vm->codes[p].ins[i].a,&vm->codes[p].ins[i].b,&vm->codes[p].ins[i].c)) { Py_DECREF(seq); goto error; }
        }
        vm->codes[p].linear=1;
        Py_ssize_t atomic_depth=0;
        for (Py_ssize_t i=0; i<vm->codes[p].count; i++) {
            int op=vm->codes[p].ins[i].op;
            if (op==OP_SPLIT || op==OP_JUMP || op==OP_LOOK || op==OP_ATOMIC_START || op==OP_ATOMIC_END || op==OP_COND || op==OP_REPEAT1) vm->codes[p].linear=0;
            if (op==OP_ATOMIC_START) {
                atomic_depth++;
                if (atomic_depth>vm->codes[p].atomic_capacity) vm->codes[p].atomic_capacity=atomic_depth;
            } else if (op==OP_ATOMIC_END && atomic_depth) atomic_depth--;
        }
        Py_DECREF(seq);
    }
    for (Py_ssize_t c=0; c<vm->class_count; c++) {
        PyObject *seq=PySequence_Fast(PySequence_Fast_GET_ITEM(cseq,c),"class must be a sequence");
        if (!seq) goto error;
        vm->classes[c].count=PySequence_Fast_GET_SIZE(seq); vm->classes[c].items=PyMem_Calloc((size_t)vm->classes[c].count,sizeof(ClassItem));
        if (!vm->classes[c].items && vm->classes[c].count) { Py_DECREF(seq); PyErr_NoMemory(); goto error; }
        for (Py_ssize_t i=0; i<vm->classes[c].count; i++) {
            int kind; unsigned int a,b;
            if (!PyArg_ParseTuple(PySequence_Fast_GET_ITEM(seq,i),"iII",&kind,&a,&b)) { Py_DECREF(seq); goto error; }
            vm->classes[c].items[i]=(ClassItem){kind,a,b};
        }
        Py_DECREF(seq);
    }
    for (Py_ssize_t p=vm->code_count; p-->0;) {
        Code *code=&vm->codes[p];
        int deterministic=1;
        int compact=1;
        for (Py_ssize_t i=0; i<code->count; i++) {
            Ins in=code->ins[i];
            if (in.op==OP_SPLIT || in.op==OP_JUMP || in.op==OP_ATOMIC_START || in.op==OP_ATOMIC_END || in.op==OP_COND) deterministic=0;
            if (in.op==OP_LOOK && (in.a<0 || in.a>=vm->code_count || !vm->codes[in.a].linear)) deterministic=0;
            if (in.op==OP_SPLIT && in.c>=0) {
                code->has_loop=1;
                Py_ssize_t close=-1;
                int consumes=0,nested=0;
                for (Py_ssize_t j=in.a; j<code->count; j++) {
                    Ins child=code->ins[j];
                    if (child.op==OP_JUMP && child.a==i) { close=j; break; }
                    if (child.op==OP_SPLIT) nested=1;
                    if (child.op==OP_CHAR || child.op==OP_DOT || child.op==OP_CAT || child.op==OP_CLASS || (child.op==OP_REPEAT1 && child.a>0)) consumes=1;
                }
                if (close<0 || nested || !consumes) compact=0;
            }
            if (in.op==OP_JUMP && in.a<=i && (in.a<0 || in.a>=code->count || code->ins[in.a].op!=OP_SPLIT || code->ins[in.a].c<0)) compact=0;
            if (in.op==OP_LOOK && (in.a<0 || in.a>=vm->code_count || (!vm->codes[in.a].linear && !vm->codes[in.a].compact))) compact=0;
            if (in.op==OP_ATOMIC_START || in.op==OP_ATOMIC_END) compact=0;
            if (in.op==OP_REPEAT1) {
                if (i+1>=code->count || in.c==1) deterministic=0;
                else if (repeat_needs_choice(vm,code,i+2,code->ins[i+1])) deterministic=0;
                else if (in.c==0) code->ins[i].c=3;
                i++;
            }
        }
        if (deterministic) code->linear=1;
        code->compact=compact;
    }
    for (Py_ssize_t p=0; p<vm->code_count; p++) {
        Code *code=&vm->codes[p];
        if (code->count<2) continue;
        Py_ssize_t length=code->count-1;
        int plain=code->ins[code->count-1].op==OP_MATCH,byte_mode=0;
        Py_UCS4 maximum=0;
        for (Py_ssize_t i=0; i<length && plain; i++) {
            Ins in=code->ins[i];
            if (in.op!=OP_CHAR || (in.b & F_I)) plain=0;
            else { if (in.b & F_BYTE) byte_mode=1; if ((Py_UCS4)in.a>maximum) maximum=(Py_UCS4)in.a; }
        }
        if (plain && length) {
            if (byte_mode) {
                code->literal=PyBytes_FromStringAndSize(NULL,length);
                if (!code->literal) goto error;
                char *data=PyBytes_AS_STRING(code->literal);
                for (Py_ssize_t i=0; i<length; i++) data[i]=(char)code->ins[i].a;
            } else {
                code->literal=PyUnicode_New(length,maximum);
                if (!code->literal) goto error;
                int kind=PyUnicode_KIND(code->literal); void *data=PyUnicode_DATA(code->literal);
                for (Py_ssize_t i=0; i<length; i++) PyUnicode_WRITE(kind,data,i,(Py_UCS4)code->ins[i].a);
            }
        }
        if (!p && code->count>=2 && code->ins[code->count-2].op==OP_ANCHOR && code->ins[code->count-2].a=='$' && !(code->ins[code->count-2].b & F_M)) {
            Py_ssize_t width=0;
            int fixed=1;
            for (Py_ssize_t i=0; i<code->count-2; i++) {
                int op=code->ins[i].op;
                if (op==OP_CHAR || op==OP_CLASS || op==OP_CAT || op==OP_DOT) width++;
                else { fixed=0; break; }
            }
            if (fixed) { code->has_suffix=1; code->suffix_width=width; }
        }
    }
    if (vm->code_count && vm->codes[0].count) {
        Code main=vm->codes[0];
        Py_ssize_t pc=0;
        while (pc<main.count && (main.ins[pc].op==OP_SAVE_START || main.ins[pc].op==OP_ANCHOR || main.ins[pc].op==OP_BOUNDARY)) pc++;
        if (pc<main.count && main.ins[pc].op==OP_SPLIT && main.ins[pc].c<0) {
            int complete=1;
            while (complete && pc>=0 && pc<main.count && vm->triple_count<128) {
                Py_ssize_t branch=pc,next=-1;
                if (main.ins[pc].op==OP_SPLIT && main.ins[pc].c<0) { branch=main.ins[pc].a; next=main.ins[pc].b; }
                unsigned char chars[3];
                for (int offset=0; offset<3; offset++) {
                    if (branch+offset>=main.count || main.ins[branch+offset].op!=OP_CHAR || (main.ins[branch+offset].b&F_I) || main.ins[branch+offset].a<0 || main.ins[branch+offset].a>255) { complete=0; break; }
                    chars[offset]=(unsigned char)main.ins[branch+offset].a;
                }
                if (!complete) break;
                uint32_t key=((uint32_t)chars[0]<<16)|((uint32_t)chars[1]<<8)|chars[2];
                int duplicate=0;
                for (int offset=0; offset<vm->triple_count; offset++) if (vm->start_triples[offset]==key) duplicate=1;
                if (!duplicate) vm->start_triples[vm->triple_count++]=key;
                if (next<0 || next<=pc || next>=main.count) { if (next>=0) complete=0; break; }
                pc=next;
            }
            if (!complete) vm->triple_count=0;
        }
    }
    if (vm->code_count && vm->codes[0].count==6) {
        Code *main=&vm->codes[0];
        Ins before_repeat=main->ins[0],before=main->ins[1],separator=main->ins[2],after_repeat=main->ins[3],after=main->ins[4];
        if (before_repeat.op==OP_REPEAT1 && before_repeat.a==0 && before_repeat.b<0 && (before.op==OP_CAT || before.op==OP_CLASS) && (separator.op==OP_CHAR || separator.op==OP_CLASS || separator.op==OP_CAT) && after_repeat.op==OP_REPEAT1 && after_repeat.a==0 && after_repeat.b<0 && (after.op==OP_CAT || after.op==OP_CLASS) && main->ins[5].op==OP_MATCH) {
            main->split_disjoint=1;
            for (Py_UCS4 value=0; value<256 && main->split_disjoint; value++) if (atom_accepts(vm,before,value) && atom_accepts(vm,separator,value)) main->split_disjoint=0;
        }
    }
    if (vm->code_count && vm->codes[0].literal) vm->literal=Py_NewRef(vm->codes[0].literal);
    vm->cache_classes=1;
    Py_DECREF(pseq); Py_DECREF(cseq);
    return PyCapsule_New(vm,"rebar.vm",capsule_free);
error:
    vm_free(vm); Py_DECREF(pseq); Py_DECREF(cseq); return NULL;
}

static int find_one(const VM *vm, const Subject *subject, Py_ssize_t pos,
                    Py_ssize_t endpos, int mode, int require_nonempty,
                    Py_ssize_t *caps, Py_ssize_t *last, Py_ssize_t *found,
                    Py_ssize_t *finish) {
    PROFILE_ADD(PROFILE_FIND,1);
    if (mode!=0 && !vm->groups && vm->code_count && vm->codes[0].count>=6) {
        Code main=vm->codes[0];
        if (main.ins[0].op==OP_SPLIT && main.ins[0].c<0 && main.ins[main.count-3].op==OP_REPEAT1 && main.ins[main.count-3].a==0 && main.ins[main.count-3].b<0 && (main.ins[main.count-3].c==0 || main.ins[main.count-3].c==3) && (main.ins[main.count-2].op==OP_CLASS || main.ins[main.count-2].op==OP_CAT || main.ins[main.count-2].op==OP_CHAR) && main.ins[main.count-1].op==OP_MATCH) {
            Py_ssize_t pc=0,join=main.count-3,branch_finish=-1;
            int valid=1;
            while (valid && pc>=0 && pc<join) {
                Py_ssize_t branch=pc,next=-1;
                if (main.ins[pc].op==OP_SPLIT && main.ins[pc].c<0) { branch=main.ins[pc].a; next=main.ins[pc].b; }
                Py_ssize_t cursor=pos,walk=branch;
                int same=1,chars=0;
                while (walk<join && main.ins[walk].op==OP_CHAR) { if (cursor>=endpos || !equal_char(subject_char(subject,cursor),(Py_UCS4)main.ins[walk].a,main.ins[walk].b)) same=0; cursor++; walk++; chars++; }
                if (!chars) { valid=0; break; }
                if (walk<join && (main.ins[walk].op!=OP_JUMP || main.ins[walk].a!=join)) { valid=0; break; }
                if (same) { branch_finish=cursor; break; }
                if (next<0) break;
                if (next<=pc || next>=join) { valid=0; break; }
                pc=next;
            }
            if (valid) {
                if (branch_finish<0) return 0;
                Py_ssize_t finish_match=branch_finish+atom_run(vm,subject,branch_finish,endpos-branch_finish,main.ins[main.count-2]);
                if (mode==2 && finish_match!=endpos) return 0;
                caps[0]=pos; caps[1]=finish_match; *last=-1; *found=pos; *finish=finish_match;
                return 1;
            }
        }
    }
    if (mode==0 && vm->groups==2 && vm->code_count && vm->codes[0].count==23) {
        Code main=vm->codes[0];
        Ins begin=main.ins[0],key_save=main.ins[1],key_first=main.ins[2],key_repeat=main.ins[3],key_rest=main.ins[4],key_end=main.ins[5],before_repeat=main.ins[6],before=main.ins[7],separator=main.ins[8],after_repeat=main.ins[9],after=main.ins[10],value_save=main.ins[11],value_repeat=main.ins[12],value=main.ins[13],value_end=main.ins[14],trail_repeat=main.ins[15],trail=main.ins[16],comment=main.ins[17];
        if (begin.op==OP_ANCHOR && begin.a=='^' && (begin.b&F_M) && key_save.op==OP_SAVE_START && key_first.op==OP_CLASS && key_repeat.op==OP_REPEAT1 && key_repeat.a==0 && key_repeat.b<0 && (key_repeat.c==0 || key_repeat.c==3) && key_rest.op==OP_CLASS && key_end.op==OP_SAVE_END && key_end.a==key_save.a && before_repeat.op==OP_REPEAT1 && before_repeat.a==0 && before_repeat.b<0 && (before_repeat.c==0 || before_repeat.c==3) && before.op==OP_CAT && separator.op==OP_CHAR && after_repeat.op==OP_REPEAT1 && after_repeat.a==0 && after_repeat.b<0 && (after_repeat.c==0 || after_repeat.c==3) && after.op==OP_CAT && value_save.op==OP_SAVE_START && value_repeat.op==OP_REPEAT1 && value_repeat.a==0 && value_repeat.b<0 && value_repeat.c==1 && value.op==OP_CLASS && value_end.op==OP_SAVE_END && value_end.a==value_save.a && trail_repeat.op==OP_REPEAT1 && trail_repeat.a==0 && trail_repeat.b<0 && (trail_repeat.c==0 || trail_repeat.c==3) && trail.op==OP_CAT && comment.op==OP_SPLIT && main.ins[18].op==OP_CHAR && main.ins[19].op==OP_REPEAT1 && main.ins[20].op==OP_DOT && main.ins[21].op==OP_ANCHOR && main.ins[21].a=='$' && main.ins[22].op==OP_MATCH) {
            int safe=1;
            for (Py_ssize_t start=pos; start<endpos; start++) {
                if (start && subject_char(subject,start-1)!='\n') continue;
                if (!class_match(vm,key_first.a,subject_char(subject,start),key_first.b,(int)key_first.c)) continue;
                Py_ssize_t key_finish=start+1+atom_run(vm,subject,start+1,endpos-start-1,key_rest),cursor=key_finish;
                Py_ssize_t before_count=atom_run(vm,subject,cursor,endpos-cursor,before);
                for (Py_ssize_t offset=0; offset<before_count; offset++) if (subject_char(subject,cursor+offset)=='\n') safe=0;
                if (!safe) break;
                cursor+=before_count;
                if (cursor>=endpos || !equal_char(subject_char(subject,cursor),(Py_UCS4)separator.a,separator.b)) continue;
                cursor++;
                Py_ssize_t after_count=atom_run(vm,subject,cursor,endpos-cursor,after);
                for (Py_ssize_t offset=0; offset<after_count; offset++) if (subject_char(subject,cursor+offset)=='\n') safe=0;
                if (!safe) break;
                cursor+=after_count;
                Py_ssize_t value_start=cursor,line_end=cursor;
                while (line_end<endpos && subject_char(subject,line_end)!='\n') line_end++;
                Py_ssize_t comment_at=line_end;
                for (Py_ssize_t offset=cursor; offset<line_end; offset++) if (equal_char(subject_char(subject,offset),(Py_UCS4)main.ins[18].a,main.ins[18].b)) { comment_at=offset; break; }
                Py_ssize_t value_finish=comment_at;
                while (value_finish>value_start && atom_match(vm,subject,value_finish-1,trail)) value_finish--;
                int valid=1;
                for (Py_ssize_t offset=value_start; valid && offset<value_finish; offset++) valid=atom_match(vm,subject,offset,value);
                if (!valid) continue;
                Py_ssize_t finish_match=line_end;
                if (line_end+1==endpos && subject_char(subject,line_end)=='\n') finish_match=endpos;
                caps[0]=start; caps[1]=finish_match;
                caps[2*key_save.a]=start; caps[2*key_save.a+1]=key_finish;
                caps[2*value_save.a]=value_start; caps[2*value_save.a+1]=value_finish;
                *last=value_save.a; *found=start; *finish=finish_match;
                return 1;
            }
            if (safe) return 0;
        }
    }
    if (mode==0 && vm->groups==2 && vm->code_count && vm->codes[0].count==36) {
        Code main=vm->codes[0];
        if (main.ins[0].op==OP_ANCHOR && main.ins[0].a=='^' && (main.ins[0].b&F_M) && main.ins[1].op==OP_SPLIT && main.ins[20].op==OP_REPEAT1 && main.ins[20].a>0 && main.ins[21].op==OP_CAT && main.ins[22].op==OP_SAVE_START && main.ins[23].op==OP_REPEAT1 && main.ins[23].a==main.ins[23].b && main.ins[24].op==OP_CLASS && main.ins[25].op==OP_REPEAT1 && main.ins[25].a==main.ins[25].b && main.ins[26].op==OP_CLASS && main.ins[27].op==OP_SAVE_END && main.ins[27].a==main.ins[22].a && main.ins[28].op==OP_REPEAT1 && main.ins[28].a>0 && main.ins[29].op==OP_CAT && main.ins[30].op==OP_SAVE_START && main.ins[31].op==OP_REPEAT1 && main.ins[31].a>0 && main.ins[32].op==OP_DOT && main.ins[33].op==OP_SAVE_END && main.ins[33].a==main.ins[30].a && main.ins[34].op==OP_ANCHOR && main.ins[34].a=='$' && main.ins[35].op==OP_MATCH) {
            int safe=1;
            for (Py_ssize_t start=pos; start<endpos; start++) {
                if (start && subject_char(subject,start-1)!='\n') continue;
                Py_ssize_t pc=1,branch_finish=-1;
                while (pc>=1 && pc<20) {
                    Py_ssize_t branch=pc,next=-1;
                    if (main.ins[pc].op==OP_SPLIT && main.ins[pc].c<0) { branch=main.ins[pc].a; next=main.ins[pc].b; }
                    Py_ssize_t cursor=start,walk=branch;
                    int same=1;
                    while (walk<20 && main.ins[walk].op==OP_CHAR) { if (cursor>=endpos || !equal_char(subject_char(subject,cursor),(Py_UCS4)main.ins[walk].a,main.ins[walk].b)) same=0; cursor++; walk++; }
                    if (same) { branch_finish=cursor; break; }
                    if (next<0 || next<=pc || next>=20) break;
                    pc=next;
                }
                if (branch_finish<0) continue;
                Py_ssize_t cursor=branch_finish,space1=atom_run(vm,subject,cursor,endpos-cursor,main.ins[21]);
                if (space1<main.ins[20].a) continue;
                for (Py_ssize_t offset=0; offset<space1; offset++) if (subject_char(subject,cursor+offset)=='\n') safe=0;
                if (!safe) break;
                cursor+=space1;
                Py_ssize_t code_start=cursor,count1=atom_run(vm,subject,cursor,endpos-cursor,main.ins[24]);
                if (count1<main.ins[23].a) continue;
                cursor+=main.ins[23].a;
                Py_ssize_t count2=atom_run(vm,subject,cursor,endpos-cursor,main.ins[26]);
                if (count2<main.ins[25].a) continue;
                cursor+=main.ins[25].a;
                Py_ssize_t code_finish=cursor,space2=atom_run(vm,subject,cursor,endpos-cursor,main.ins[29]);
                if (space2<main.ins[28].a) continue;
                for (Py_ssize_t offset=0; offset<space2; offset++) if (subject_char(subject,cursor+offset)=='\n') safe=0;
                if (!safe) break;
                cursor+=space2;
                Py_ssize_t text_start=cursor,text_count=atom_run(vm,subject,cursor,endpos-cursor,main.ins[32]);
                if (text_count<main.ins[31].a) continue;
                Py_ssize_t text_finish=cursor+text_count;
                if (text_finish<endpos && subject_char(subject,text_finish)!='\n') continue;
                caps[0]=start; caps[1]=text_finish;
                caps[2*main.ins[22].a]=code_start; caps[2*main.ins[22].a+1]=code_finish;
                caps[2*main.ins[30].a]=text_start; caps[2*main.ins[30].a+1]=text_finish;
                *last=main.ins[30].a; *found=start; *finish=text_finish;
                return 1;
            }
            if (safe) return 0;
        }
    }
    if (mode==0 && vm->groups==1 && vm->code_count && vm->codes[0].count==11) {
        Code main=vm->codes[0];
        Ins opening=main.ins[0],save=main.ins[1],first=main.ins[2],rest_repeat=main.ins[3],rest=main.ins[4],end=main.ins[5],boundary=main.ins[6],tail_repeat=main.ins[7],tail=main.ins[8],closing=main.ins[9];
        if (opening.op==OP_CHAR && save.op==OP_SAVE_START && save.a==1 && first.op==OP_CLASS && rest_repeat.op==OP_REPEAT1 && rest_repeat.a==0 && rest_repeat.b<0 && (rest_repeat.c==0 || rest_repeat.c==3) && rest.op==OP_CLASS && end.op==OP_SAVE_END && end.a==1 && boundary.op==OP_BOUNDARY && boundary.a && tail_repeat.op==OP_REPEAT1 && tail_repeat.a==0 && tail_repeat.b<0 && (tail_repeat.c==0 || tail_repeat.c==3) && tail.op==OP_CLASS && closing.op==OP_CHAR && main.ins[10].op==OP_MATCH && !atom_accepts(vm,tail,(Py_UCS4)closing.a)) {
            for (Py_ssize_t start=pos; start+2<=endpos; start++) {
                if (!equal_char(subject_char(subject,start),(Py_UCS4)opening.a,opening.b) || !class_match(vm,first.a,subject_char(subject,start+1),first.b,(int)first.c)) continue;
                Py_ssize_t tag_end=start+2;
                tag_end+=atom_run(vm,subject,tag_end,endpos-tag_end,rest);
                int left=category(subject_char(subject,tag_end-1),'w',boundary.b),right=tag_end<endpos && category(subject_char(subject,tag_end),'w',boundary.b);
                if (left==right) continue;
                Py_ssize_t cursor=tag_end;
                cursor+=atom_run(vm,subject,cursor,endpos-cursor,tail);
                if (cursor>=endpos || !equal_char(subject_char(subject,cursor),(Py_UCS4)closing.a,closing.b)) continue;
                caps[0]=start; caps[1]=cursor+1; caps[2]=start+1; caps[3]=tag_end; *last=1; *found=start; *finish=cursor+1;
                return 1;
            }
            return 0;
        }
    }
    if (mode==0 && vm->groups==1 && vm->code_count && vm->codes[0].count>=7) {
        Code main=vm->codes[0];
        Py_ssize_t prefix_end=0;
        while (prefix_end<main.count && main.ins[prefix_end].op==OP_CHAR) prefix_end++;
        if (prefix_end>0 && prefix_end+4<main.count && main.ins[prefix_end].op==OP_SAVE_START && main.ins[prefix_end].a==1 && main.ins[prefix_end+1].op==OP_REPEAT1 && main.ins[prefix_end+1].c==1 && main.ins[prefix_end+2].op==OP_DOT && main.ins[prefix_end+3].op==OP_SAVE_END && main.ins[prefix_end+3].a==1 && main.ins[main.count-1].op==OP_MATCH) {
            Py_ssize_t suffix_begin=prefix_end+4,suffix_end=main.count-1;
            int fixed=suffix_begin<suffix_end;
            for (Py_ssize_t pc=suffix_begin; fixed && pc<suffix_end; pc++) fixed=main.ins[pc].op==OP_CHAR;
            if (fixed) {
                Ins repeat=main.ins[prefix_end+1],dot=main.ins[prefix_end+2];
                Py_ssize_t prefix_width=prefix_end,suffix_width=suffix_end-suffix_begin;
                for (Py_ssize_t start=pos; start+prefix_width+repeat.a+suffix_width<=endpos; start++) {
                    int prefix_ok=1;
                    for (Py_ssize_t offset=0; prefix_ok && offset<prefix_width; offset++) prefix_ok=equal_char(subject_char(subject,start+offset),(Py_UCS4)main.ins[offset].a,main.ins[offset].b);
                    if (!prefix_ok) continue;
                    Py_ssize_t body=start+prefix_width,first=body+repeat.a,last_body=endpos-suffix_width;
                    if (repeat.b>=0 && last_body>body+repeat.b) last_body=body+repeat.b;
                    int allowed=1;
                    for (Py_ssize_t finish_body=first; finish_body<=last_body; finish_body++) {
                        if (!(dot.a&F_S) && finish_body>body && subject_char(subject,finish_body-1)=='\n') allowed=0;
                        if (!allowed) break;
                        int suffix_ok=1;
                        for (Py_ssize_t offset=0; suffix_ok && offset<suffix_width; offset++) suffix_ok=equal_char(subject_char(subject,finish_body+offset),(Py_UCS4)main.ins[suffix_begin+offset].a,main.ins[suffix_begin+offset].b);
                        if (!suffix_ok) continue;
                        Py_ssize_t finish_match=finish_body+suffix_width;
                        if (require_nonempty && start==pos && finish_match==start) continue;
                        caps[0]=start; caps[1]=finish_match; caps[2]=body; caps[3]=finish_body; *last=1; *found=start; *finish=finish_match;
                        return 1;
                    }
                }
                return 0;
            }
        }
    }
    if (mode==0 && vm->groups==2 && vm->code_count && vm->codes[0].count==9) {
        Code main=vm->codes[0];
        Ins open_save=main.ins[0],opening=main.ins[1],open_end=main.ins[2],body_save=main.ins[3],repeat=main.ins[4],dot=main.ins[5],body_end=main.ins[6],closing=main.ins[7];
        if (open_save.op==OP_SAVE_START && opening.op==OP_CLASS && open_end.op==OP_SAVE_END && open_end.a==open_save.a && body_save.op==OP_SAVE_START && repeat.op==OP_REPEAT1 && repeat.a==0 && repeat.b<0 && repeat.c==1 && dot.op==OP_DOT && body_end.op==OP_SAVE_END && body_end.a==body_save.a && closing.op==OP_BACKREF && closing.a==open_save.a && main.ins[8].op==OP_MATCH) {
            for (Py_ssize_t start=pos; start<endpos; start++) {
                Py_UCS4 open=subject_char(subject,start);
                if (!class_match(vm,opening.a,open,opening.b,(int)opening.c)) continue;
                for (Py_ssize_t close=start+1; close<endpos; close++) {
                    Py_UCS4 value=subject_char(subject,close);
                    if (!(dot.a&F_S) && value=='\n') break;
                    if (!equal_char(value,open,closing.b)) continue;
                    caps[0]=start; caps[1]=close+1;
                    caps[2*open_save.a]=start; caps[2*open_save.a+1]=start+1;
                    caps[2*body_save.a]=start+1; caps[2*body_save.a+1]=close;
                    *last=body_save.a; *found=start; *finish=close+1;
                    return 1;
                }
            }
            return 0;
        }
    }
    if (mode==0 && vm->groups==2 && vm->code_count && vm->codes[0].count==15) {
        Code main=vm->codes[0];
        Ins first_save=main.ins[0],first=main.ins[1],rest_repeat=main.ins[2],rest=main.ins[3],first_end=main.ins[4],before_repeat=main.ins[5],before=main.ins[6],separator=main.ins[7],after_repeat=main.ins[8],after=main.ins[9],second_save=main.ins[10],value_repeat=main.ins[11],value=main.ins[12],second_end=main.ins[13];
        if (first_save.op==OP_SAVE_START && first.op==OP_CLASS && rest_repeat.op==OP_REPEAT1 && rest_repeat.a==0 && rest_repeat.b<0 && (rest_repeat.c==0 || rest_repeat.c==3) && rest.op==OP_CLASS && first_end.op==OP_SAVE_END && first_end.a==first_save.a && before_repeat.op==OP_REPEAT1 && before_repeat.a==0 && before_repeat.b<0 && (before_repeat.c==0 || before_repeat.c==3) && (before.op==OP_CAT || before.op==OP_CLASS) && separator.op==OP_CHAR && after_repeat.op==OP_REPEAT1 && after_repeat.a==0 && after_repeat.b<0 && (after_repeat.c==0 || after_repeat.c==3) && (after.op==OP_CAT || after.op==OP_CLASS) && second_save.op==OP_SAVE_START && value_repeat.op==OP_REPEAT1 && value_repeat.a>0 && value_repeat.b<0 && (value_repeat.c==0 || value_repeat.c==3) && (value.op==OP_CLASS || value.op==OP_CAT) && second_end.op==OP_SAVE_END && second_end.a==second_save.a && main.ins[14].op==OP_MATCH && !atom_accepts(vm,rest,(Py_UCS4)separator.a) && !atom_accepts(vm,before,(Py_UCS4)separator.a)) {
            for (Py_ssize_t start=pos; start<endpos; start++) {
                if (!class_match(vm,first.a,subject_char(subject,start),first.b,(int)first.c)) continue;
                Py_ssize_t key_end=start+1;
                key_end+=atom_run(vm,subject,key_end,endpos-key_end,rest);
                Py_ssize_t cursor=key_end;
                cursor+=atom_run(vm,subject,cursor,endpos-cursor,before);
                if (cursor>=endpos || !equal_char(subject_char(subject,cursor),(Py_UCS4)separator.a,separator.b)) { start=key_end-1; continue; }
                cursor++;
                cursor+=atom_run(vm,subject,cursor,endpos-cursor,after);
                Py_ssize_t value_start=cursor,count=atom_run(vm,subject,cursor,endpos-cursor,value);
                cursor+=count;
                if (count<value_repeat.a) { start=key_end-1; continue; }
                caps[0]=start; caps[1]=cursor;
                caps[2*first_save.a]=start; caps[2*first_save.a+1]=key_end;
                caps[2*second_save.a]=value_start; caps[2*second_save.a+1]=cursor;
                *last=second_save.a; *found=start; *finish=cursor;
                return 1;
            }
            return 0;
        }
    }
    if (mode==0 && !vm->groups && vm->code_count && vm->codes[0].count==5) {
        Code main=vm->codes[0];
        Ins split=main.ins[0],jump=main.ins[2];
        Ins look=main.ins[1].op==OP_LOOK ? main.ins[1] : main.ins[3],boundary=main.ins[1].op==OP_BOUNDARY ? main.ins[1] : main.ins[3];
        if (split.op==OP_SPLIT && split.a==1 && split.b==3 && jump.op==OP_JUMP && jump.a==4 && look.op==OP_LOOK && !(look.b&2) && boundary.op==OP_BOUNDARY && main.ins[4].op==OP_MATCH && look.a>=0 && look.a<vm->code_count) {
            Code child=vm->codes[look.a];
            if (child.count==2 && child.ins[1].op==OP_MATCH && (child.ins[0].op==OP_CHAR || child.ins[0].op==OP_DOT || child.ins[0].op==OP_CAT || child.ins[0].op==OP_CLASS)) {
                for (Py_ssize_t cursor=pos; cursor<=endpos; cursor++) {
                    if (require_nonempty && cursor==pos) continue;
                    int ahead=cursor<endpos && atom_match(vm,subject,cursor,child.ins[0]);
                    int left=cursor>0 && category(subject_char(subject,cursor-1),'w',boundary.b);
                    int right=cursor<endpos && category(subject_char(subject,cursor),'w',boundary.b);
                    int edge=((left!=right)==!!boundary.a);
                    if (ahead==!!(look.b&1) || edge) {
                        caps[0]=cursor; caps[1]=cursor; *last=-1; *found=cursor; *finish=cursor;
                        return 1;
                    }
                }
                return 0;
            }
        }
    }
    if (mode==0 && !vm->groups && vm->code_count>1 && vm->codes[0].count==3) {
        Code main=vm->codes[0];
        Ins separator=main.ins[0],look=main.ins[1];
        if (separator.op==OP_CHAR && look.op==OP_LOOK && (look.b&3)==1 && main.ins[2].op==OP_MATCH && look.a>=0 && look.a<vm->code_count) {
            Code child=vm->codes[look.a];
            if (child.count==12 && child.ins[0].op==OP_SPLIT && child.ins[0].a==1 && child.ins[0].b==8 && child.ins[0].c==8 && child.ins[1].op==OP_REPEAT1 && child.ins[1].a==0 && child.ins[1].b<0 && child.ins[2].op==OP_CLASS && child.ins[2].c==1 && child.ins[3].op==OP_CHAR && child.ins[4].op==OP_REPEAT1 && child.ins[4].a==0 && child.ins[4].b<0 && child.ins[5].op==OP_CLASS && child.ins[5].c==1 && child.ins[6].op==OP_CHAR && child.ins[7].op==OP_JUMP && child.ins[7].a==0 && child.ins[8].op==OP_REPEAT1 && child.ins[8].a==0 && child.ins[8].b<0 && child.ins[9].op==OP_CLASS && child.ins[9].c==1 && child.ins[10].op==OP_ANCHOR && child.ins[10].a=='$' && child.ins[11].op==OP_MATCH && child.ins[3].a==child.ins[6].a && child.ins[3].a!=separator.a) {
                Py_UCS4 quote=(Py_UCS4)child.ins[3].a;
                int exact=1;
                for (int index=0; index<3; index++) {
                    Ins atom=child.ins[index==0 ? 2 : index==1 ? 5 : 9];
                    if (atom.a<0 || atom.a>=vm->class_count) { exact=0; break; }
                    CharClass cls=vm->classes[atom.a];
                    if (cls.count!=1 || cls.items[0].kind!=1 || cls.items[0].a!=quote) { exact=0; break; }
                }
                if (exact) {
                    int even=1;
                    Py_ssize_t found_separator=-1;
                    for (Py_ssize_t cursor=endpos; cursor-->pos;) {
                        Py_UCS4 value=subject_char(subject,cursor);
                        if (equal_char(value,quote,child.ins[3].b)) even=!even;
                        else if (even && equal_char(value,(Py_UCS4)separator.a,separator.b)) found_separator=cursor;
                    }
                    if (found_separator<0) return 0;
                    caps[0]=found_separator; caps[1]=found_separator+1; *last=-1; *found=found_separator; *finish=found_separator+1;
                    return 1;
                }
            }
        }
    }
    if (mode==0 && !vm->groups && vm->code_count>1 && vm->codes[0].count==7) {
        Code main=vm->codes[0];
        Ins left_edge=main.ins[0],look=main.ins[1],first=main.ins[2],repeat=main.ins[3],rest=main.ins[4],right_edge=main.ins[5];
        if (left_edge.op==OP_BOUNDARY && left_edge.a && look.op==OP_LOOK && (look.b&3)==0 && first.op==OP_CLASS && repeat.op==OP_REPEAT1 && repeat.a==0 && repeat.b<0 && (repeat.c==0 || repeat.c==3) && rest.op==OP_CLASS && right_edge.op==OP_BOUNDARY && right_edge.a && main.ins[6].op==OP_MATCH && look.a>=0 && look.a<vm->code_count && vm->codes[look.a].literal) {
            Code forbidden=vm->codes[look.a];
            Py_ssize_t width=subject->byte_mode ? PyBytes_GET_SIZE(forbidden.literal) : PyUnicode_GET_LENGTH(forbidden.literal);
            for (Py_ssize_t cursor=pos; cursor<endpos; cursor++) {
                int left=cursor>0 && category(subject_char(subject,cursor-1),'w',left_edge.b);
                int right=category(subject_char(subject,cursor),'w',left_edge.b);
                if (left==right || !class_match(vm,first.a,subject_char(subject,cursor),first.b,(int)first.c)) continue;
                int excluded=cursor+width<=endpos;
                for (Py_ssize_t offset=0; excluded && offset<width; offset++) {
                    Py_UCS4 value=subject_char(subject,cursor+offset),wanted;
                    if (subject->byte_mode) wanted=(unsigned char)PyBytes_AS_STRING(forbidden.literal)[offset];
                    else wanted=PyUnicode_READ_CHAR(forbidden.literal,offset);
                    excluded=equal_char(value,wanted,forbidden.ins[offset].b);
                }
                if (excluded) continue;
                Py_ssize_t finish_token=cursor+1;
                finish_token+=atom_run(vm,subject,finish_token,endpos-finish_token,rest);
                int end_left=category(subject_char(subject,finish_token-1),'w',right_edge.b);
                int end_right=finish_token<endpos && category(subject_char(subject,finish_token),'w',right_edge.b);
                if (end_left==end_right) continue;
                caps[0]=cursor; caps[1]=finish_token; *last=-1; *found=cursor; *finish=finish_token;
                return 1;
            }
            return 0;
        }
    }
    if (mode==0 && vm->code_count && vm->groups>=2 && vm->codes[0].count==10) {
        Code code=vm->codes[0];
        Ins save1=code.ins[0],repeat1=code.ins[1],atom1=code.ins[2],end1=code.ins[3],separator=code.ins[4],save2=code.ins[5],repeat2=code.ins[6],atom2=code.ins[7],end2=code.ins[8];
        if (save1.op==OP_SAVE_START && repeat1.op==OP_REPEAT1 && repeat1.a>0 && (repeat1.c==0 || repeat1.c==3) && end1.op==OP_SAVE_END && end1.a==save1.a && separator.op==OP_CHAR && save2.op==OP_SAVE_START && repeat2.op==OP_REPEAT1 && repeat2.a>0 && (repeat2.c==0 || repeat2.c==3) && end2.op==OP_SAVE_END && end2.a==save2.a && code.ins[9].op==OP_MATCH && !atom_accepts(vm,atom1,(Py_UCS4)separator.a)) {
            Py_ssize_t cursor=pos;
            while (cursor<endpos) {
                while (cursor<endpos && !atom_match(vm,subject,cursor,atom1)) cursor++;
                if (cursor>=endpos) return 0;
                Py_ssize_t start=cursor,maximum1=repeat1.b<0 ? endpos-cursor : repeat1.b;
                if (maximum1>endpos-cursor) maximum1=endpos-cursor;
                Py_ssize_t count1=atom_run(vm,subject,cursor,maximum1,atom1);
                cursor+=count1;
                if (count1<repeat1.a || cursor>=endpos || !atom_match(vm,subject,cursor,separator)) continue;
                Py_ssize_t second_start=++cursor,maximum2=repeat2.b<0 ? endpos-cursor : repeat2.b;
                if (maximum2>endpos-cursor) maximum2=endpos-cursor;
                Py_ssize_t count2=atom_run(vm,subject,cursor,maximum2,atom2);
                cursor+=count2;
                if (count2<repeat2.a || (require_nonempty && start==pos && cursor==start)) continue;
                for (Py_ssize_t i=0; i<2*(vm->groups+1); i++) caps[i]=-1;
                caps[0]=start; caps[1]=cursor;
                caps[2*save1.a]=start; caps[2*save1.a+1]=start+count1;
                caps[2*save2.a]=second_start; caps[2*save2.a+1]=second_start+count2;
                *last=save2.a; *found=start; *finish=cursor;
                return 1;
            }
            return 0;
        }
    }
    if (mode==0 && vm->literal) {
        Py_ssize_t length=subject->byte_mode ? PyBytes_GET_SIZE(vm->literal) : PyUnicode_GET_LENGTH(vm->literal);
        Py_ssize_t start=-1;
        if (subject->byte_mode) {
            const char *hay=subject->bytes,*needle=PyBytes_AS_STRING(vm->literal);
            Py_ssize_t cursor=pos,last_start=endpos-length;
            while (cursor<=last_start) {
                const char *found_byte=memchr(hay+cursor,(unsigned char)needle[0],(size_t)(last_start-cursor+1));
                if (!found_byte) break;
                cursor=(Py_ssize_t)(found_byte-hay);
                if (!memcmp(hay+cursor,needle,(size_t)length)) { start=cursor; break; }
                cursor++;
            }
        } else start=PyUnicode_Find(subject->obj,vm->literal,pos,endpos,1);
        if (start<-1) return -2;
        if (start<0) return 0;
        caps[0]=start; caps[1]=start+length; *last=-1; *found=start; *finish=start+length;
        return 1;
    }
    if (mode==0 && vm->code_count && vm->codes[0].count>1 && vm->codes[0].ins[0].op==OP_LOOK) {
        Code main=vm->codes[0];
        Ins look=main.ins[0];
        if ((look.b & 1) && (look.b & 2) && look.a>=0 && look.a<vm->code_count && vm->codes[look.a].literal) {
            PyObject *prefix=vm->codes[look.a].literal;
            Py_ssize_t width=subject->byte_mode ? PyBytes_GET_SIZE(prefix) : PyUnicode_GET_LENGTH(prefix);
            Py_ssize_t cursor=pos>width ? pos-width : 0;
            while (cursor<=endpos-width) {
                Py_ssize_t pivot=-1;
                if (subject->byte_mode) {
                    const char *hay=subject->bytes,*needle=PyBytes_AS_STRING(prefix);
                    Py_ssize_t final_start=endpos-width;
                    while (cursor<=final_start) {
                        const char *found_byte=memchr(hay+cursor,(unsigned char)needle[0],(size_t)(final_start-cursor+1));
                        if (!found_byte) break;
                        cursor=(Py_ssize_t)(found_byte-hay);
                        if (!memcmp(hay+cursor,needle,(size_t)width)) { pivot=cursor; break; }
                        cursor++;
                    }
                } else pivot=PyUnicode_Find(subject->obj,prefix,cursor,endpos,1);
                if (pivot<-1) return -2;
                if (pivot<0) return 0;
                Py_ssize_t start=pivot+width;
                if (start>=pos) {
                    for (Py_ssize_t i=0; i<2*(vm->groups+1); i++) caps[i]=-1;
                    caps[0]=start; *last=-1; *finish=-1;
                    int got=execute(vm,0,subject,start,endpos,caps,last,finish,0,require_nonempty && start==pos,0);
                    if (got<0) return got;
                    if (got) { caps[1]=*finish; *found=start; return 1; }
                }
                cursor=pivot+1;
            }
            return 0;
        }
    }
    if (mode==0 && !vm->groups && vm->code_count && vm->codes[0].count>3) {
        Code main=vm->codes[0];
        Py_ssize_t repeat_pc=0;
        while (repeat_pc<main.count && main.ins[repeat_pc].op==OP_SAVE_START) repeat_pc++;
        if (repeat_pc+2<main.count && main.ins[repeat_pc].op==OP_REPEAT1 && main.ins[repeat_pc].a>0 && (main.ins[repeat_pc].c==0 || main.ins[repeat_pc].c==3)) {
            Ins repeat=main.ins[repeat_pc],atom=main.ins[repeat_pc+1];
            Py_ssize_t delimiter_pc=repeat_pc+2;
            while (delimiter_pc<main.count && main.ins[delimiter_pc].op==OP_SAVE_END) delimiter_pc++;
            if (delimiter_pc<main.count && main.ins[delimiter_pc].op==OP_CHAR && !atom_accepts(vm,atom,(Py_UCS4)main.ins[delimiter_pc].a)) {
                Ins delimiter=main.ins[delimiter_pc];
                Py_ssize_t cursor=pos+repeat.a;
                while (cursor<endpos) {
                    Py_ssize_t pivot=-1;
                    if (subject->byte_mode) {
                        const char *data=subject->bytes,*found_byte=memchr(data+cursor,(unsigned char)delimiter.a,(size_t)(endpos-cursor));
                        if (found_byte) pivot=(Py_ssize_t)(found_byte-data);
                    } else pivot=PyUnicode_FindChar(subject->obj,(Py_UCS4)delimiter.a,cursor,endpos,1);
                    if (pivot<-1) return -2;
                    if (pivot<0) return 0;
                    Py_ssize_t start=pivot;
                    while (start>pos && atom_match(vm,subject,start-1,atom)) start--;
                    if (pivot-start>=repeat.a && (repeat.b<0 || pivot-start<=repeat.b)) {
                        for (Py_ssize_t i=0; i<2*(vm->groups+1); i++) caps[i]=-1;
                        caps[0]=start; *last=-1; *finish=-1;
                        int got=execute(vm,0,subject,start,endpos,caps,last,finish,0,require_nonempty && start==pos,0);
                        if (got<0) return got;
                        if (got) { caps[1]=*finish; *found=start; return 1; }
                    }
                    cursor=pivot+1;
                }
                return 0;
            }
        }
    }
    Py_ssize_t first_start = pos, last_start = mode==0 ? endpos : pos;
    if (mode==0 && vm->code_count && vm->codes[0].has_suffix) {
        Code main=vm->codes[0];
        first_start=endpos-main.suffix_width;
        last_start=first_start;
        if (endpos>pos && subject_char(subject,endpos-1)=='\n') first_start--;
    }
    if (mode==0 && vm->code_count && vm->codes[0].count) {
        Ins first=vm->codes[0].ins[0];
        if (first.op==OP_LOOK && (first.b&3)==3 && first_start<first.c) first_start=first.c;
    }
    for (Py_ssize_t start=first_start; start<=last_start; start++) {
        PROFILE_ADD(PROFILE_START,1);
        if (start<pos || start>endpos) continue;
        if (mode==0 && vm->code_count && vm->codes[0].count && start<endpos) {
            Code main=vm->codes[0];
            Py_ssize_t first_pc=0;
            while (first_pc<main.count && main.ins[first_pc].op==OP_SAVE_START) first_pc++;
            Ins first=main.ins[first_pc];
            if (first.op==OP_REPEAT1 && first.a>0 && first_pc+1<main.count) first=main.ins[++first_pc];
            if (first.op==OP_LOOK && (first.b & 1) && (first.b & 2) && first.a>=0 && first.a<vm->code_count) {
                Code look=vm->codes[first.a];
                if (look.linear && start>=first.c) {
                    int possible=1;
                    Py_ssize_t check=start-first.c;
                    for (Py_ssize_t pc=0; pc<look.count-1; pc++) {
                        Ins atom=look.ins[pc];
                        if (atom.op==OP_CHAR || atom.op==OP_CLASS || atom.op==OP_CAT || atom.op==OP_DOT) {
                            if (!atom_match(vm,subject,check++,atom)) { possible=0; break; }
                        } else { possible=1; break; }
                    }
                    if (!possible) continue;
                } else if (start<first.c) continue;
            }
            if (first.op==OP_ANCHOR && (first.a=='^' || first.a=='A')) {
                if (first.a=='A' && start!=0) continue;
                if (first.a=='^' && start!=0 && (!(first.b & F_M) || subject_char(subject,start-1)!='\n')) continue;
                if (first_pc+1<main.count) first=main.ins[++first_pc];
            }
            Py_UCS4 value = subject_char(subject,start);
            if (first.op==OP_CHAR) {
                if (!(first.b&F_I) && value!=(Py_UCS4)first.a && first.a>=0 && first.a<=255 && (subject->byte_mode || subject->unicode_kind==PyUnicode_1BYTE_KIND)) {
                    const unsigned char *data=subject->byte_mode ? (const unsigned char *)subject->bytes : (const unsigned char *)subject->unicode_data;
                    const unsigned char *pivot=memchr(data+start,(unsigned char)first.a,(size_t)(last_start-start+1));
                    if (!pivot) return 0;
                    start=(Py_ssize_t)(pivot-data);
                    value=(Py_UCS4)first.a;
                }
                if (!equal_char(value,(Py_UCS4)first.a,first.b)) { PROFILE_ADD(PROFILE_START_REJECT,1); continue; }
            }
            else if (first.op==OP_CLASS) { if (!class_match(vm,first.a,value,first.b,(int)first.c)) { PROFILE_ADD(PROFILE_START_REJECT,1); continue; } }
            else if (first.op==OP_CAT) { if (!category(value,first.a,first.b)) { PROFILE_ADD(PROFILE_START_REJECT,1); continue; } }
            else {
                if (!start_accepts(vm,value)) { PROFILE_ADD(PROFILE_START_REJECT,1); continue; }
                if (vm->start_pairs && value<256 && start+1<endpos) {
                    Py_UCS4 next=subject_char(subject,start+1);
                    if (next<256) {
                        Py_ssize_t bit=((Py_ssize_t)value<<8)|next;
                        if (!(vm->start_pairs[bit>>6]&((uint64_t)1<<(bit&63)))) { PROFILE_ADD(PROFILE_PAIR_REJECT,1); continue; }
                    }
                }
                if (vm->triple_count && value<256 && start+2<endpos) {
                    Py_UCS4 second=subject_char(subject,start+1),third=subject_char(subject,start+2);
                    if (second<256 && third<256) {
                        uint32_t key=((uint32_t)value<<16)|((uint32_t)second<<8)|(uint32_t)third;
                        int accepted=0;
                        for (int offset=0; offset<vm->triple_count && !accepted; offset++) accepted=vm->start_triples[offset]==key;
                        if (!accepted) { PROFILE_ADD(PROFILE_PAIR_REJECT,1); continue; }
                    }
                }
            }
        }
        for (Py_ssize_t i=0; i<2*(vm->groups+1); i++) caps[i]=-1;
        caps[0]=start;
        *last=-1; *finish=-1;
        int got=execute(vm,0,subject,start,endpos,caps,last,finish,mode==2,require_nonempty && start==pos,0);
        if (got<0) return got;
        if (got) {
            caps[1]=*finish; *found=start;
            return 1;
        }
        if (mode!=0) break;
    }
    return 0;
}

static int subject_init(Subject *subject, PyObject *string) {
    subject->obj=string; subject->byte_mode=0; subject->unicode_kind=0; subject->length=0; subject->bytes=NULL; subject->unicode_data=NULL;
    if (PyBytes_Check(string)) { subject->byte_mode=1; subject->length=PyBytes_GET_SIZE(string); subject->bytes=PyBytes_AS_STRING(string); }
    else if (PyByteArray_Check(string)) { subject->byte_mode=1; subject->length=PyByteArray_GET_SIZE(string); subject->bytes=PyByteArray_AS_STRING(string); }
    else if (PyMemoryView_Check(string)) {
        Py_buffer *view=PyMemoryView_GET_BUFFER(string);
        if (!PyBuffer_IsContiguous(view,'C')) { PyErr_Format(PyExc_TypeError,"expected string or bytes-like object, got '%.80s'",Py_TYPE(string)->tp_name); return 0; }
        subject->byte_mode=1; subject->length=view->len; subject->bytes=(const char *)view->buf;
    }
    else if (PyUnicode_Check(string)) { subject->length=PyUnicode_GET_LENGTH(string); subject->unicode_kind=PyUnicode_KIND(string); subject->unicode_data=PyUnicode_DATA(string); }
    else {
        Py_buffer view;
        if (PyObject_GetBuffer(string,&view,PyBUF_SIMPLE)<0) {
            PyErr_Clear();
            PyErr_Format(PyExc_TypeError,"expected string or bytes-like object, got '%.80s'",Py_TYPE(string)->tp_name);
            return 0;
        }
        if (!PyBuffer_IsContiguous(&view,'C')) {
            PyBuffer_Release(&view);
            PyErr_Format(PyExc_TypeError,"expected string or bytes-like object, got '%.80s'",Py_TYPE(string)->tp_name);
            return 0;
        }
        subject->byte_mode=1; subject->length=view.len; subject->bytes=(const char *)view.buf;
        PyBuffer_Release(&view);
    }
    return 1;
}

static PyObject *subject_slice(const Subject *subject, Py_ssize_t begin, Py_ssize_t end) {
    if (begin<0) begin=0;
    if (begin>subject->length) begin=subject->length;
    if (end<begin) end=begin;
    if (end>subject->length) end=subject->length;
    if (subject->byte_mode) return PyBytes_FromStringAndSize(subject->bytes+begin,end-begin);
    return PyUnicode_Substring(subject->obj,begin,end);
}

static PyObject *span_list(const VM *vm, const Py_ssize_t *caps) {
    PyObject *spans=PyList_New(vm->groups+1);
    if (!spans) return NULL;
    for (Py_ssize_t g=0; g<=vm->groups; g++) {
        PyObject *item;
        if (caps[2*g]<0) item=Py_NewRef(Py_None);
        else item=Py_BuildValue("(nn)",caps[2*g],caps[2*g+1]);
        if (!item) { Py_DECREF(spans); return NULL; }
        PyList_SET_ITEM(spans,g,item);
    }
    return spans;
}

static PyObject *native_match(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *capsule,*string;
    Py_ssize_t pos,endpos;
    int mode,require_nonempty;
    if (!PyArg_ParseTuple(args,"OOnnii",&capsule,&string,&pos,&endpos,&mode,&require_nonempty)) return NULL;
    VM *vm=PyCapsule_GetPointer(capsule,"rebar.vm");
    if (!vm) return NULL;
    Subject subject;
    if (!subject_init(&subject,string)) return NULL;
    if (pos<0) pos=0;
    if (endpos<0) endpos=0;
    if (endpos>subject.length) endpos=subject.length;
    if (pos>endpos) Py_RETURN_NONE;
    Py_ssize_t *caps=PyMem_Malloc((size_t)(2*(vm->groups+1))*sizeof(Py_ssize_t));
    if (!caps) return PyErr_NoMemory();
    Py_ssize_t last=-1,found=-1,finish=-1;
    int got=find_one(vm,&subject,pos,endpos,mode,require_nonempty,caps,&last,&found,&finish);
    if (got<0) { PyMem_Free(caps); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
    if (!got) { PyMem_Free(caps); Py_RETURN_NONE; }
    PyObject *spans=span_list(vm,caps);
    if (!spans) { PyMem_Free(caps); return NULL; }
    PyObject *last_obj=last<0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t(last);
    if (!last_obj) { Py_DECREF(spans); PyMem_Free(caps); return NULL; }
    PyObject *result=Py_BuildValue("nnOO",found,finish,spans,last_obj);
    Py_DECREF(spans); Py_DECREF(last_obj); PyMem_Free(caps); return result;
}

static PyObject *collect_core(VM *vm, Subject subject, Py_ssize_t pos, Py_ssize_t endpos, Py_ssize_t limit, int mode) {
    if (pos<0) pos=0;
    if (endpos<0) endpos=0;
    if (endpos>subject.length) endpos=subject.length;
    if (pos>endpos) pos=endpos+1;
    PyObject *output=PyList_New(0);
    if (!output) return NULL;
    if (mode==1 && !vm->groups && vm->code_count && vm->codes[0].count==6) {
        Code main=vm->codes[0];
        Ins before_repeat=main.ins[0],before=main.ins[1],separator=main.ins[2],after_repeat=main.ins[3],after=main.ins[4];
        if (before_repeat.op==OP_REPEAT1 && before_repeat.a==0 && before_repeat.b<0 && (before_repeat.c==0 || before_repeat.c==3) && (before.op==OP_CAT || before.op==OP_CLASS) && (separator.op==OP_CHAR || separator.op==OP_CLASS || separator.op==OP_CAT) && after_repeat.op==OP_REPEAT1 && after_repeat.a==0 && after_repeat.b<0 && (after_repeat.c==0 || after_repeat.c==3) && (after.op==OP_CAT || after.op==OP_CLASS) && main.ins[5].op==OP_MATCH) {
            if (main.split_disjoint) {
                Py_ssize_t previous=pos,cursor=pos,matches=0;
                while (cursor<endpos && (!limit || matches<limit)) {
                    if (!atom_match(vm,&subject,cursor,separator)) { cursor++; continue; }
                    Py_ssize_t begin=cursor;
                    while (begin>previous && atom_match(vm,&subject,begin-1,before)) begin--;
                    Py_ssize_t finish=cursor+1+atom_run(vm,&subject,cursor+1,endpos-cursor-1,after);
                    PyObject *piece=subject_slice(&subject,previous,begin);
                    if (!piece || PyList_Append(output,piece)<0) { Py_XDECREF(piece); Py_DECREF(output); return NULL; }
                    Py_DECREF(piece); previous=finish; cursor=finish; matches++;
                }
                PyObject *tail=subject_slice(&subject,previous,subject.length);
                if (!tail || PyList_Append(output,tail)<0) { Py_XDECREF(tail); Py_DECREF(output); return NULL; }
                Py_DECREF(tail);
                return output;
            }
        }
    }
    if (mode==0 && !vm->groups && vm->code_count && vm->codes[0].count==22) {
        Code main=vm->codes[0];
        if (main.ins[0].op==OP_SPLIT && main.ins[1].op==OP_ANCHOR && main.ins[1].a=='^' && main.ins[3].op==OP_CAT && main.ins[4].op==OP_SPLIT && main.ins[5].op==OP_SPLIT && main.ins[6].op==OP_CHAR && main.ins[7].op==OP_CHAR && main.ins[8].op==OP_CHAR && main.ins[10].op==OP_CHAR && main.ins[11].op==OP_REPEAT1 && main.ins[11].a>0 && main.ins[11].b<0 && main.ins[12].op==OP_CLASS && main.ins[13].op==OP_CHAR && main.ins[14].op==OP_REPEAT1 && main.ins[14].a>0 && main.ins[14].b<0 && main.ins[15].op==OP_CLASS && main.ins[16].op==OP_SPLIT && main.ins[17].op==OP_CHAR && main.ins[18].op==OP_REPEAT1 && main.ins[18].a>0 && main.ins[18].b<0 && main.ins[19].op==OP_CLASS && main.ins[20].op==OP_JUMP && main.ins[21].op==OP_MATCH) {
            Py_ssize_t cursor=pos,matches=0;
            while (cursor<endpos && (!limit || matches<limit)) {
                int at_begin=cursor==0,space=!at_begin && category(subject_char(&subject,cursor),main.ins[3].a,main.ins[3].b);
                if (!at_begin && !space) { cursor++; continue; }
                Py_ssize_t start=cursor,here=cursor+(space ? 1 : 0),without_prefix=here;
                if (here+3<=endpos && equal_char(subject_char(&subject,here),(Py_UCS4)main.ins[6].a,main.ins[6].b) && equal_char(subject_char(&subject,here+1),(Py_UCS4)main.ins[7].a,main.ins[7].b) && equal_char(subject_char(&subject,here+2),(Py_UCS4)main.ins[8].a,main.ins[8].b)) here+=3;
                else if (here<endpos && equal_char(subject_char(&subject,here),(Py_UCS4)main.ins[10].a,main.ins[10].b)) here++;
                Py_ssize_t first=atom_run(vm,&subject,here,endpos-here,main.ins[12]);
                if (first<main.ins[11].a || here+first>=endpos || !equal_char(subject_char(&subject,here+first),(Py_UCS4)main.ins[13].a,main.ins[13].b)) {
                    if (here==without_prefix) { cursor++; continue; }
                    here=without_prefix;
                    first=atom_run(vm,&subject,here,endpos-here,main.ins[12]);
                    if (first<main.ins[11].a || here+first>=endpos || !equal_char(subject_char(&subject,here+first),(Py_UCS4)main.ins[13].a,main.ins[13].b)) { cursor++; continue; }
                }
                here+=first;
                here++;
                Py_ssize_t second=atom_run(vm,&subject,here,endpos-here,main.ins[15]);
                if (second<main.ins[14].a) { cursor++; continue; }
                here+=second;
                while (here<endpos && equal_char(subject_char(&subject,here),(Py_UCS4)main.ins[17].a,main.ins[17].b)) {
                    Py_ssize_t count=atom_run(vm,&subject,here+1,endpos-here-1,main.ins[19]);
                    if (count<main.ins[18].a) break;
                    here+=1+count;
                }
                PyObject *piece=subject_slice(&subject,start,here);
                if (!piece || PyList_Append(output,piece)<0) { Py_XDECREF(piece); Py_DECREF(output); return NULL; }
                Py_DECREF(piece); matches++; cursor=here;
            }
            return output;
        }
    }
    if (mode==0 && !vm->groups && vm->code_count && vm->codes[0].count>=5) {
        Code main=vm->codes[0];
        Py_ssize_t prefix=0;
        while (prefix<main.count && main.ins[prefix].op==OP_CHAR) prefix++;
        if (prefix>0 && prefix+4==main.count && main.ins[prefix].op==OP_REPEAT1 && main.ins[prefix].a==0 && main.ins[prefix].b<0 && (main.ins[prefix].c==0 || main.ins[prefix].c==3) && (main.ins[prefix+1].op==OP_CLASS || main.ins[prefix+1].op==OP_CAT || main.ins[prefix+1].op==OP_DOT) && main.ins[prefix+2].op==OP_ANCHOR && main.ins[prefix+2].a=='$' && main.ins[prefix+3].op==OP_MATCH) {
            Ins repeat=main.ins[prefix],atom=main.ins[prefix+1],anchor=main.ins[prefix+2];
            Py_ssize_t cursor=pos,matches=0;
            while (cursor+prefix<=endpos && (!limit || matches<limit)) {
                int prefix_ok=1;
                for (Py_ssize_t offset=0; prefix_ok && offset<prefix; offset++) prefix_ok=equal_char(subject_char(&subject,cursor+offset),(Py_UCS4)main.ins[offset].a,main.ins[offset].b);
                if (!prefix_ok) { cursor++; continue; }
                Py_ssize_t finish=cursor+prefix,count=atom_run(vm,&subject,finish,endpos-finish,atom);
                finish+=count;
                if (count<repeat.a) { cursor++; continue; }
                int anchored=finish==endpos || (finish+1==endpos && finish<subject.length && subject_char(&subject,finish)=='\n') || ((anchor.b&F_M) && finish<endpos && subject_char(&subject,finish)=='\n');
                if (!anchored) { cursor++; continue; }
                PyObject *piece=subject_slice(&subject,cursor,finish);
                if (!piece || PyList_Append(output,piece)<0) { Py_XDECREF(piece); Py_DECREF(output); return NULL; }
                Py_DECREF(piece); matches++; cursor=finish==cursor ? cursor+1 : finish;
            }
            return output;
        }
    }
    if (mode==1 && !vm->groups && vm->code_count>1 && vm->codes[0].count==3) {
        Code main=vm->codes[0];
        Ins separator=main.ins[0],look=main.ins[1];
        if (separator.op==OP_CHAR && look.op==OP_LOOK && (look.b&3)==1 && main.ins[2].op==OP_MATCH && look.a>=0 && look.a<vm->code_count) {
            Code child=vm->codes[look.a];
            if (child.count==12 && child.ins[0].op==OP_SPLIT && child.ins[0].a==1 && child.ins[0].b==8 && child.ins[0].c==8 && child.ins[1].op==OP_REPEAT1 && child.ins[1].a==0 && child.ins[1].b<0 && child.ins[2].op==OP_CLASS && child.ins[2].c==1 && child.ins[3].op==OP_CHAR && child.ins[4].op==OP_REPEAT1 && child.ins[4].a==0 && child.ins[4].b<0 && child.ins[5].op==OP_CLASS && child.ins[5].c==1 && child.ins[6].op==OP_CHAR && child.ins[7].op==OP_JUMP && child.ins[7].a==0 && child.ins[8].op==OP_REPEAT1 && child.ins[8].a==0 && child.ins[8].b<0 && child.ins[9].op==OP_CLASS && child.ins[9].c==1 && child.ins[10].op==OP_ANCHOR && child.ins[10].a=='$' && child.ins[11].op==OP_MATCH && child.ins[3].a==child.ins[6].a && child.ins[3].a!=separator.a) {
                Py_UCS4 quote=(Py_UCS4)child.ins[3].a;
                int exact=1;
                for (int index=0; index<3; index++) {
                    Ins atom=child.ins[index==0 ? 2 : index==1 ? 5 : 9];
                    if (atom.a<0 || atom.a>=vm->class_count) { exact=0; break; }
                    CharClass cls=vm->classes[atom.a];
                    if (cls.count!=1 || cls.items[0].kind!=1 || cls.items[0].a!=quote) { exact=0; break; }
                }
                if (exact) {
                    int total=0,prefix=0;
                    for (Py_ssize_t cursor=pos; cursor<endpos; cursor++) if (equal_char(subject_char(&subject,cursor),quote,child.ins[3].b)) total=!total;
                    Py_ssize_t previous=pos,matches=0;
                    for (Py_ssize_t cursor=pos; cursor<endpos && (!limit || matches<limit); cursor++) {
                        Py_UCS4 value=subject_char(&subject,cursor);
                        if (equal_char(value,quote,child.ins[3].b)) { prefix=!prefix; continue; }
                        if (prefix!=total || !equal_char(value,(Py_UCS4)separator.a,separator.b)) continue;
                        PyObject *piece=subject_slice(&subject,previous,cursor);
                        if (!piece || PyList_Append(output,piece)<0) { Py_XDECREF(piece); Py_DECREF(output); return NULL; }
                        Py_DECREF(piece); previous=cursor+1; matches++;
                    }
                    PyObject *tail=subject_slice(&subject,previous,subject.length);
                    if (!tail || PyList_Append(output,tail)<0) { Py_XDECREF(tail); Py_DECREF(output); return NULL; }
                    Py_DECREF(tail);
                    return output;
                }
            }
        }
    }
    if (mode==0 && !vm->groups && vm->code_count>1 && vm->codes[0].count==7) {
        Code main=vm->codes[0];
        Ins left_edge=main.ins[0],look=main.ins[1],first=main.ins[2],repeat=main.ins[3],rest=main.ins[4],right_edge=main.ins[5];
        if (left_edge.op==OP_BOUNDARY && left_edge.a && look.op==OP_LOOK && (look.b&3)==0 && first.op==OP_CLASS && repeat.op==OP_REPEAT1 && repeat.a==0 && repeat.b<0 && (repeat.c==0 || repeat.c==3) && rest.op==OP_CLASS && right_edge.op==OP_BOUNDARY && right_edge.a && main.ins[6].op==OP_MATCH && look.a>=0 && look.a<vm->code_count && vm->codes[look.a].literal) {
            Code forbidden=vm->codes[look.a];
            Py_ssize_t width=subject.byte_mode ? PyBytes_GET_SIZE(forbidden.literal) : PyUnicode_GET_LENGTH(forbidden.literal);
            Py_ssize_t cursor=pos,matches=0;
            while (cursor<endpos && (!limit || matches<limit)) {
                int left=cursor>0 && category(subject_char(&subject,cursor-1),'w',left_edge.b);
                int right=category(subject_char(&subject,cursor),'w',left_edge.b);
                if (left==right || !class_match(vm,first.a,subject_char(&subject,cursor),first.b,(int)first.c)) { cursor++; continue; }
                int excluded=cursor+width<=endpos;
                for (Py_ssize_t offset=0; excluded && offset<width; offset++) {
                    Py_UCS4 value=subject_char(&subject,cursor+offset),wanted;
                    if (subject.byte_mode) wanted=(unsigned char)PyBytes_AS_STRING(forbidden.literal)[offset];
                    else wanted=PyUnicode_READ_CHAR(forbidden.literal,offset);
                    excluded=equal_char(value,wanted,forbidden.ins[offset].b);
                }
                Py_ssize_t finish=cursor+1;
                finish+=atom_run(vm,&subject,finish,endpos-finish,rest);
                int end_left=category(subject_char(&subject,finish-1),'w',right_edge.b);
                int end_right=finish<endpos && category(subject_char(&subject,finish),'w',right_edge.b);
                if (!excluded && end_left!=end_right) {
                    PyObject *piece=subject_slice(&subject,cursor,finish);
                    if (!piece || PyList_Append(output,piece)<0) { Py_XDECREF(piece); Py_DECREF(output); return NULL; }
                    Py_DECREF(piece); matches++;
                }
                cursor=finish;
            }
            return output;
        }
    }
    if (mode==1 && vm->groups==1 && vm->code_count && vm->codes[0].count==4) {
        Code code=vm->codes[0];
        if (code.ins[0].op==OP_SAVE_START && code.ins[0].a==1 && code.ins[2].op==OP_SAVE_END && code.ins[2].a==1 && code.ins[3].op==OP_MATCH && (code.ins[1].op==OP_CHAR || code.ins[1].op==OP_DOT || code.ins[1].op==OP_CAT || code.ins[1].op==OP_CLASS)) {
            Py_ssize_t cursor=pos,previous=pos,matches=0;
            Ins atom=code.ins[1];
            while (cursor<endpos && (!limit || matches<limit)) {
                if (!atom_match(vm,&subject,cursor,atom)) { cursor++; continue; }
                PyObject *prefix=subject_slice(&subject,previous,cursor),*capture=subject_slice(&subject,cursor,cursor+1);
                if (!prefix || !capture || PyList_Append(output,prefix)<0 || PyList_Append(output,capture)<0) { Py_XDECREF(prefix); Py_XDECREF(capture); Py_DECREF(output); return NULL; }
                Py_DECREF(prefix); Py_DECREF(capture); matches++; previous=++cursor;
            }
            PyObject *tail=subject_slice(&subject,previous,subject.length);
            if (!tail || PyList_Append(output,tail)<0) { Py_XDECREF(tail); Py_DECREF(output); return NULL; }
            Py_DECREF(tail);
            return output;
        }
    }
    if (mode==0 && !vm->groups && vm->code_count && vm->codes[0].count>=7) {
        Code code=vm->codes[0];
        Ins repeats[32],atoms[32];
        Py_ssize_t branches=0,pc=0,terminal=code.count-1;
        int runs=code.ins[terminal].op==OP_MATCH;
        while (runs && pc<terminal && branches<32) {
            Py_ssize_t branch_pc=pc,next_pc=terminal;
            if (code.ins[pc].op==OP_SPLIT && code.ins[pc].c<0) { branch_pc=code.ins[pc].a; next_pc=code.ins[pc].b; }
            if (branch_pc+1>=terminal || code.ins[branch_pc].op!=OP_REPEAT1 || code.ins[branch_pc].a<1) { runs=0; break; }
            repeats[branches]=code.ins[branch_pc]; atoms[branches]=code.ins[branch_pc+1]; branches++;
            Py_ssize_t after=branch_pc+2;
            if (next_pc==terminal) { if (after!=terminal) runs=0; break; }
            if (after>=terminal || code.ins[after].op!=OP_JUMP || code.ins[after].a!=terminal || next_pc<=pc || next_pc>=terminal) { runs=0; break; }
            pc=next_pc;
        }
        if (runs && branches>1) {
            Py_ssize_t cursor=pos,matches=0;
            while (cursor<endpos && (!limit || matches<limit)) {
                Py_ssize_t finish=-1;
                for (Py_ssize_t branch=0; branch<branches; branch++) {
                    Ins repeat=repeats[branch],atom=atoms[branch];
                    Py_ssize_t maximum=repeat.b<0 ? endpos-cursor : repeat.b;
                    if (maximum>endpos-cursor) maximum=endpos-cursor;
                    Py_ssize_t matched=atom_run(vm,&subject,cursor,maximum,atom);
                    if (matched>=repeat.a) { finish=cursor+(repeat.c==1 ? repeat.a : matched); break; }
                }
                if (finish<0) { cursor++; continue; }
                PyObject *item=subject_slice(&subject,cursor,finish);
                if (!item || PyList_Append(output,item)<0) { Py_XDECREF(item); Py_DECREF(output); return NULL; }
                Py_DECREF(item); matches++; cursor=finish;
            }
            return output;
        }
        Py_ssize_t repeat_pc=-1;
        int simple=code.ins[terminal].op==OP_MATCH;
        for (Py_ssize_t i=0; i<terminal && simple; i++) {
            Ins in=code.ins[i];
            if (in.op==OP_REPEAT1 && i+1<terminal && repeat_pc<0) { repeat_pc=i; i++; continue; }
            if (in.op!=OP_CHAR && in.op!=OP_DOT && in.op!=OP_CAT && in.op!=OP_CLASS) simple=0;
        }
        if (simple && repeat_pc>=0 && repeat_pc+2==terminal) {
            Py_ssize_t cursor=pos,matches=0;
            while (cursor<endpos && (!limit || matches<limit)) {
                Py_ssize_t start=cursor,here=cursor;
                int matched_prefix=1;
                for (Py_ssize_t pc=0; pc<repeat_pc; pc++) {
                    if (here>=endpos || !atom_match(vm,&subject,here,code.ins[pc])) { matched_prefix=0; break; }
                    here++;
                }
                if (!matched_prefix) { cursor++; continue; }
                Ins repeat=code.ins[repeat_pc],atom=code.ins[repeat_pc+1];
                Py_ssize_t maximum=repeat.b<0 ? endpos-here : repeat.b;
                if (maximum>endpos-here) maximum=endpos-here;
                Py_ssize_t repeated=atom_run(vm,&subject,here,maximum,atom);
                if (repeated<repeat.a) { cursor++; continue; }
                here+=repeat.c==1 ? repeat.a : repeated;
                PyObject *item=subject_slice(&subject,start,here);
                if (!item || PyList_Append(output,item)<0) { Py_XDECREF(item); Py_DECREF(output); return NULL; }
                Py_DECREF(item); matches++; cursor=here;
            }
            return output;
        }
        if (code.count==7 && code.ins[0].op==OP_REPEAT1 && code.ins[0].a>0 && (code.ins[0].c==0 || code.ins[0].c==3) && code.ins[2].op==OP_SPLIT && code.ins[2].c<0 && code.ins[2].a==3 && code.ins[2].b==6 && code.ins[3].op==OP_CHAR && code.ins[4].op==OP_REPEAT1 && code.ins[4].a>0 && (code.ins[4].c==0 || code.ins[4].c==3) && code.ins[6].op==OP_MATCH && !atom_accepts(vm,code.ins[1],(Py_UCS4)code.ins[3].a)) {
            Py_ssize_t cursor=pos,matches=0;
            Ins first_repeat=code.ins[0],first_atom=code.ins[1],delimiter=code.ins[3],second_repeat=code.ins[4],second_atom=code.ins[5];
            while (cursor<endpos && (!limit || matches<limit)) {
                if (!atom_match(vm,&subject,cursor,first_atom)) { cursor++; continue; }
                Py_ssize_t start=cursor,first_max=first_repeat.b<0 ? endpos-cursor : first_repeat.b;
                if (first_max>endpos-cursor) first_max=endpos-cursor;
                Py_ssize_t first_count=atom_run(vm,&subject,cursor,first_max,first_atom);
                if (first_count<first_repeat.a) { cursor++; continue; }
                Py_ssize_t finish=cursor+first_count;
                if (finish<endpos && atom_match(vm,&subject,finish,delimiter)) {
                    Py_ssize_t after=finish+1,second_max=second_repeat.b<0 ? endpos-after : second_repeat.b;
                    if (second_max>endpos-after) second_max=endpos-after;
                    Py_ssize_t second_count=atom_run(vm,&subject,after,second_max,second_atom);
                    if (second_count>=second_repeat.a) finish=after+second_count;
                }
                PyObject *item=subject_slice(&subject,start,finish);
                if (!item || PyList_Append(output,item)<0) { Py_XDECREF(item); Py_DECREF(output); return NULL; }
                Py_DECREF(item); matches++; cursor=finish;
            }
            return output;
        }
    }
    Py_ssize_t local_caps[34];
    Py_ssize_t cap_count=2*(vm->groups+1);
    Py_ssize_t *caps=cap_count<=34 ? local_caps : PyMem_Malloc((size_t)cap_count*sizeof(Py_ssize_t));
    if (!caps) { Py_DECREF(output); return PyErr_NoMemory(); }
    Py_ssize_t cursor=pos,previous=pos,matches=0;
    int nonempty=0;
    while (cursor<=endpos && (!limit || matches<limit)) {
        Py_ssize_t last=-1,found=-1,finish=-1;
        int got=find_one(vm,&subject,cursor,endpos,0,nonempty,caps,&last,&found,&finish);
        if (got<0) { if (caps!=local_caps) PyMem_Free(caps); Py_DECREF(output); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
        if (!got) break;
        PyObject *item=NULL;
        if (mode==0) {
            if (!vm->groups) item=subject_slice(&subject,found,finish);
            else if (vm->groups==1) item=caps[2]<0 ? subject_slice(&subject,0,0) : subject_slice(&subject,caps[2],caps[3]);
            else {
                item=PyTuple_New(vm->groups);
                if (item) for (Py_ssize_t g=1; g<=vm->groups; g++) {
                    PyObject *part=caps[2*g]<0 ? subject_slice(&subject,0,0) : subject_slice(&subject,caps[2*g],caps[2*g+1]);
                    if (!part) { Py_CLEAR(item); break; }
                    PyTuple_SET_ITEM(item,g-1,part);
                }
            }
        } else if (mode==1) {
            item=subject_slice(&subject,previous,found);
            if (!item || PyList_Append(output,item)<0) { Py_XDECREF(item); if (caps!=local_caps) PyMem_Free(caps); Py_DECREF(output); return NULL; }
            Py_DECREF(item); item=NULL;
            for (Py_ssize_t g=1; g<=vm->groups; g++) {
                item=caps[2*g]<0 ? Py_NewRef(Py_None) : subject_slice(&subject,caps[2*g],caps[2*g+1]);
                if (!item || PyList_Append(output,item)<0) { Py_XDECREF(item); if (caps!=local_caps) PyMem_Free(caps); Py_DECREF(output); return NULL; }
                Py_DECREF(item); item=NULL;
            }
            previous=finish;
        } else {
            PyObject *spans=span_list(vm,caps);
            PyObject *last_obj=last<0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t(last);
            if (!spans || !last_obj) { Py_XDECREF(spans); Py_XDECREF(last_obj); if (caps!=local_caps) PyMem_Free(caps); Py_DECREF(output); return NULL; }
            item=PyTuple_Pack(2,spans,last_obj);
            Py_DECREF(spans); Py_DECREF(last_obj);
        }
        if (mode!=1) {
            if (!item || PyList_Append(output,item)<0) { Py_XDECREF(item); if (caps!=local_caps) PyMem_Free(caps); Py_DECREF(output); return NULL; }
            Py_DECREF(item);
        }
        matches++;
        if (found==finish) { cursor=found; nonempty=1; }
        else { cursor=finish; nonempty=0; }
    }
    if (caps!=local_caps) PyMem_Free(caps);
    if (mode==1) {
        PyObject *tail=subject_slice(&subject,previous,subject.length);
        if (!tail || PyList_Append(output,tail)<0) { Py_XDECREF(tail); Py_DECREF(output); return NULL; }
        Py_DECREF(tail);
    }
    return output;
}

static PyObject *native_collect(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *capsule,*string;
    Py_ssize_t pos,endpos,limit;
    int mode;
    if (!PyArg_ParseTuple(args,"OOnnni",&capsule,&string,&pos,&endpos,&limit,&mode)) return NULL;
    VM *vm=PyCapsule_GetPointer(capsule,"rebar.vm");
    if (!vm) return NULL;
    Subject subject;
    if (!subject_init(&subject,string)) return NULL;
    return collect_core(vm,subject,pos,endpos,limit,mode);
}

typedef struct {
    PyObject_HEAD
    PyObject *pattern, *groupindex, *capsule, *templates;
    VM *vm;
    Py_ssize_t flags, groups;
} PatternObject;

typedef struct {
    PyObject_VAR_HEAD
    PatternObject *pattern;
    PyObject *string;
    Py_ssize_t pos, endpos, lastindex;
    Py_ssize_t caps[];
} MatchObject;

typedef struct {
    PyObject_HEAD
    PatternObject *pattern;
    PyObject *string;
    Py_ssize_t cursor, endpos, original_pos;
    int nonempty, done;
    Py_buffer view;
    Subject subject;
    int has_view;
} FindIterObject;

static PyTypeObject PatternType;
static PyTypeObject MatchType;
static PyTypeObject FindIterType;
static PyTypeObject ScannerType;
static PyObject *template_function=NULL;
static PyObject *template_compiler=NULL;

static int pattern_subject(PatternObject *pattern, PyObject *string, Subject *subject) {
    if (!subject_init(subject,string)) return 0;
    if (PyUnicode_Check(pattern->pattern) && subject->byte_mode) {
        PyErr_SetString(PyExc_TypeError,"cannot use a string pattern on a bytes-like object"); return 0;
    }
    if (PyBytes_Check(pattern->pattern) && !subject->byte_mode) {
        PyErr_SetString(PyExc_TypeError,"cannot use a bytes pattern on a string-like object"); return 0;
    }
    return 1;
}

static MatchObject *match_alloc(PatternObject *pattern, PyObject *string, Py_ssize_t pos, Py_ssize_t endpos) {
    Py_ssize_t cap_count=2*(pattern->groups+1);
    MatchObject *match=(MatchObject *)PyType_GenericAlloc(&MatchType,cap_count);
    if (!match) return NULL;
    match->pattern=pattern; Py_INCREF(pattern);
    match->string=string; Py_INCREF(string);
    match->pos=pos; match->endpos=endpos; match->lastindex=-1;
    return match;
}

static int match_number(MatchObject *match, PyObject *value, Py_ssize_t *number) {
    if (PyUnicode_Check(value)) {
        PyObject *index=PyDict_GetItemWithError(match->pattern->groupindex,value);
        if (!index) { if (!PyErr_Occurred()) PyErr_SetString(PyExc_IndexError,"no such group"); return 0; }
        *number=PyLong_AsSsize_t(index);
        return !PyErr_Occurred();
    }
    PyObject *index=PyNumber_Index(value);
    if (!index) { PyErr_Clear(); PyErr_SetString(PyExc_IndexError,"no such group"); return 0; }
    *number=PyLong_AsSsize_t(index);
    Py_DECREF(index);
    if (PyErr_Occurred()) { PyErr_Clear(); PyErr_SetString(PyExc_IndexError,"no such group"); return 0; }
    if (*number<0 || *number>match->pattern->groups) { PyErr_SetString(PyExc_IndexError,"no such group"); return 0; }
    return 1;
}

static PyObject *match_piece(MatchObject *match, Py_ssize_t number, PyObject *default_value) {
    Py_ssize_t begin=match->caps[2*number],end=match->caps[2*number+1];
    if (begin<0) return Py_NewRef(default_value);
    Subject subject;
    if (!subject_init(&subject,match->string)) return NULL;
    return subject_slice(&subject,begin,end);
}

static PyObject *match_group(MatchObject *match, PyObject *args) {
    Py_ssize_t count=PyTuple_GET_SIZE(args);
    if (!count) return match_piece(match,0,Py_None);
    if (count==1) {
        Py_ssize_t number;
        if (!match_number(match,PyTuple_GET_ITEM(args,0),&number)) return NULL;
        return match_piece(match,number,Py_None);
    }
    PyObject *result=PyTuple_New(count);
    if (!result) return NULL;
    for (Py_ssize_t i=0; i<count; i++) {
        Py_ssize_t number;
        if (!match_number(match,PyTuple_GET_ITEM(args,i),&number)) { Py_DECREF(result); return NULL; }
        PyObject *value=match_piece(match,number,Py_None);
        if (!value) { Py_DECREF(result); return NULL; }
        PyTuple_SET_ITEM(result,i,value);
    }
    return result;
}

static PyObject *match_groups(MatchObject *match, PyObject *args, PyObject *kwargs) {
    static char *names[]={"default",NULL};
    PyObject *default_value=Py_None;
    if (!PyArg_ParseTupleAndKeywords(args,kwargs,"|O:groups",names,&default_value)) return NULL;
    PyObject *result=PyTuple_New(match->pattern->groups);
    if (!result) return NULL;
    for (Py_ssize_t g=1; g<=match->pattern->groups; g++) {
        PyObject *value=match_piece(match,g,default_value);
        if (!value) { Py_DECREF(result); return NULL; }
        PyTuple_SET_ITEM(result,g-1,value);
    }
    return result;
}

static PyObject *match_groupdict(MatchObject *match, PyObject *args, PyObject *kwargs) {
    static char *names[]={"default",NULL};
    PyObject *default_value=Py_None;
    if (!PyArg_ParseTupleAndKeywords(args,kwargs,"|O:groupdict",names,&default_value)) return NULL;
    PyObject *result=PyDict_New();
    if (!result) return NULL;
    PyObject *key,*index;
    Py_ssize_t cursor=0;
    while (PyDict_Next(match->pattern->groupindex,&cursor,&key,&index)) {
        Py_ssize_t number=PyLong_AsSsize_t(index);
        if (PyErr_Occurred()) { Py_DECREF(result); return NULL; }
        PyObject *value=match_piece(match,number,default_value);
        if (!value || PyDict_SetItem(result,key,value)<0) { Py_XDECREF(value); Py_DECREF(result); return NULL; }
        Py_DECREF(value);
    }
    return result;
}

static PyObject *match_bound(MatchObject *match, PyObject *args, int which) {
    PyObject *group=NULL;
    if (!PyArg_ParseTuple(args,"|O",&group)) return NULL;
    Py_ssize_t number=0;
    if (group && !match_number(match,group,&number)) return NULL;
    Py_ssize_t begin=match->caps[2*number],end=match->caps[2*number+1];
    if (which==0) return PyLong_FromSsize_t(begin<0 ? -1 : begin);
    if (which==1) return PyLong_FromSsize_t(begin<0 ? -1 : end);
    return Py_BuildValue("(nn)",begin<0 ? -1 : begin,begin<0 ? -1 : end);
}

static PyObject *match_start(MatchObject *match, PyObject *args) { return match_bound(match,args,0); }
static PyObject *match_end(MatchObject *match, PyObject *args) { return match_bound(match,args,1); }
static PyObject *match_span(MatchObject *match, PyObject *args) { return match_bound(match,args,2); }

static PyObject *match_expand(MatchObject *match, PyObject *template) {
    PyObject *owned_key=NULL,*template_key=template;
    if (PyByteArray_Check(template) || PyMemoryView_Check(template)) {
        owned_key=PyBytes_FromObject(template);
        if (!owned_key) return NULL;
        template_key=owned_key;
    }
    if (PyObject_Hash(template_key)==-1 && PyErr_Occurred()) { Py_XDECREF(owned_key); return NULL; }
    int byte_mode=PyBytes_Check(template_key);
    if (!template_compiler) { Py_XDECREF(owned_key); PyErr_SetString(PyExc_RuntimeError,"native template compiler is not configured"); return NULL; }
    PyObject *parts=PyDict_GetItemWithError(match->pattern->templates,template_key);
    if (!parts && PyErr_Occurred()) { Py_XDECREF(owned_key); return NULL; }
    if (!parts) {
        PyObject *byte_value=byte_mode ? Py_True : Py_False;
        parts=PyObject_CallFunctionObjArgs(template_compiler,template_key,(PyObject *)match->pattern,byte_value,NULL);
        if (!parts) { Py_XDECREF(owned_key); return NULL; }
        if (PyDict_SetItem(match->pattern->templates,template_key,parts)<0) { Py_DECREF(parts); Py_XDECREF(owned_key); return NULL; }
        Py_DECREF(parts);
        parts=PyDict_GetItemWithError(match->pattern->templates,template_key);
        if (!parts) { Py_XDECREF(owned_key); return NULL; }
    }
    Py_XDECREF(owned_key);
    Py_ssize_t count=PyTuple_GET_SIZE(parts);
    if (!byte_mode && PyUnicode_Check(match->string)) {
        PyUnicodeWriter *writer=PyUnicodeWriter_Create(16);
        if (!writer) return NULL;
        for (Py_ssize_t index=0; index<count; index++) {
            PyObject *part=PyTuple_GET_ITEM(parts,index);
            int written;
            if (PyLong_Check(part)) {
                Py_ssize_t number=PyLong_AsSsize_t(part);
                if (PyErr_Occurred()) { PyUnicodeWriter_Discard(writer); return NULL; }
                Py_ssize_t begin=match->caps[2*number],end=match->caps[2*number+1];
                written=begin<0 ? 0 : PyUnicodeWriter_WriteSubstring(writer,match->string,begin,end);
            } else written=PyUnicodeWriter_WriteStr(writer,part);
            if (written<0) { PyUnicodeWriter_Discard(writer); return NULL; }
        }
        return PyUnicodeWriter_Finish(writer);
    }
    PyObject *pieces=PyList_New(count);
    if (!pieces) return NULL;
    for (Py_ssize_t i=0; i<count; i++) {
        PyObject *part=PyTuple_GET_ITEM(parts,i),*value=NULL;
        if (PyLong_Check(part)) {
            Py_ssize_t number=PyLong_AsSsize_t(part);
            if (PyErr_Occurred()) { Py_DECREF(pieces); return NULL; }
            value=match_piece(match,number,Py_None);
            if (value==Py_None) { Py_SETREF(value,byte_mode ? PyBytes_FromStringAndSize("",0) : PyUnicode_New(0,127)); }
        } else value=Py_NewRef(part);
        if (!value) { Py_DECREF(pieces); return NULL; }
        PyList_SET_ITEM(pieces,i,value);
    }
    PyObject *empty=byte_mode ? PyBytes_FromStringAndSize("",0) : PyUnicode_New(0,127);
    if (!empty) { Py_DECREF(pieces); return NULL; }
    PyObject *result=byte_mode ? PyBytes_Join(empty,pieces) : PyUnicode_Join(empty,pieces);
    Py_DECREF(empty); Py_DECREF(pieces);
    return result;
}

static PyObject *match_copy(MatchObject *match, PyObject *ignored) { (void)ignored; return Py_NewRef(match); }
static PyObject *match_deepcopy(MatchObject *match, PyObject *memo) { (void)memo; return Py_NewRef(match); }
static PyObject *match_reduce(MatchObject *match, PyObject *ignored) { (void)match; (void)ignored; PyErr_SetString(PyExc_TypeError,"cannot pickle 're.Match' object"); return NULL; }
static PyObject *match_class_getitem(PyObject *type, PyObject *item) { return Py_GenericAlias(type,item); }

static PyObject *match_repr(MatchObject *match) {
    PyObject *value=match_piece(match,0,Py_None);
    if (!value) return NULL;
    PyObject *result=PyUnicode_FromFormat("<re.Match object; span=(%zd, %zd), match=%.50R>",match->caps[0],match->caps[1],value);
    Py_DECREF(value);
    return result;
}

static PyObject *match_subscript(PyObject *value, PyObject *key) {
    MatchObject *match=(MatchObject *)value;
    Py_ssize_t number;
    if (!match_number(match,key,&number)) return NULL;
    return match_piece(match,number,Py_None);
}

static PyObject *match_get_re(MatchObject *match, void *closure) { (void)closure; return Py_NewRef(match->pattern); }
static PyObject *match_get_string(MatchObject *match, void *closure) { (void)closure; return Py_NewRef(match->string); }
static PyObject *match_get_pos(MatchObject *match, void *closure) { (void)closure; return PyLong_FromSsize_t(match->pos); }
static PyObject *match_get_endpos(MatchObject *match, void *closure) { (void)closure; return PyLong_FromSsize_t(match->endpos); }
static PyObject *match_get_lastindex(MatchObject *match, void *closure) { (void)closure; return match->lastindex<0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t(match->lastindex); }

static PyObject *match_get_lastgroup(MatchObject *match, void *closure) {
    (void)closure;
    if (match->lastindex<0) Py_RETURN_NONE;
    PyObject *key,*index;
    Py_ssize_t cursor=0;
    while (PyDict_Next(match->pattern->groupindex,&cursor,&key,&index)) if (PyLong_AsSsize_t(index)==match->lastindex) return Py_NewRef(key);
    Py_RETURN_NONE;
}

static PyObject *match_get_regs(MatchObject *match, void *closure) {
    (void)closure;
    PyObject *result=PyTuple_New(match->pattern->groups+1);
    if (!result) return NULL;
    for (Py_ssize_t g=0; g<=match->pattern->groups; g++) {
        Py_ssize_t begin=match->caps[2*g],end=match->caps[2*g+1];
        PyObject *item=Py_BuildValue("(nn)",begin<0 ? -1 : begin,begin<0 ? -1 : end);
        if (!item) { Py_DECREF(result); return NULL; }
        PyTuple_SET_ITEM(result,g,item);
    }
    return result;
}

static void match_dealloc(MatchObject *match) { Py_XDECREF(match->pattern); Py_XDECREF(match->string); Py_TYPE(match)->tp_free((PyObject *)match); }

static PyMethodDef MatchMethods[]={
    {"group",(PyCFunction)match_group,METH_VARARGS,"Return one or more captured groups."},
    {"groups",(PyCFunction)(void(*)(void))match_groups,METH_VARARGS|METH_KEYWORDS,"Return all captured groups."},
    {"groupdict",(PyCFunction)(void(*)(void))match_groupdict,METH_VARARGS|METH_KEYWORDS,"Return named captured groups."},
    {"start",(PyCFunction)match_start,METH_VARARGS,"Return the start of a group."},
    {"end",(PyCFunction)match_end,METH_VARARGS,"Return the end of a group."},
    {"span",(PyCFunction)match_span,METH_VARARGS,"Return the span of a group."},
    {"expand",(PyCFunction)match_expand,METH_O,"Expand a replacement template."},
    {"__copy__",(PyCFunction)match_copy,METH_NOARGS,"Return the immutable match."},
    {"__deepcopy__",(PyCFunction)match_deepcopy,METH_O,"Return the immutable match."},
    {"__reduce__",(PyCFunction)match_reduce,METH_NOARGS,"Matches cannot be pickled."},
    {"__reduce_ex__",(PyCFunction)match_reduce,METH_O,"Matches cannot be pickled."},
    {"__class_getitem__",(PyCFunction)match_class_getitem,METH_O|METH_CLASS,"Return a generic match alias."},
    {NULL,NULL,0,NULL}
};

static PyGetSetDef MatchGetSet[]={
    {"re",(getter)match_get_re,NULL,"Compiled pattern.",NULL},{"string",(getter)match_get_string,NULL,"Input string.",NULL},
    {"pos",(getter)match_get_pos,NULL,"Search start.",NULL},{"endpos",(getter)match_get_endpos,NULL,"Search end.",NULL},
    {"lastindex",(getter)match_get_lastindex,NULL,"Last matched group index.",NULL},{"lastgroup",(getter)match_get_lastgroup,NULL,"Last matched group name.",NULL},
    {"regs",(getter)match_get_regs,NULL,"Captured spans.",NULL},{NULL,NULL,NULL,NULL,NULL}
};

static PyMappingMethods MatchMapping={0,match_subscript,0};

static PyTypeObject MatchType={
    PyVarObject_HEAD_INIT(NULL,0)
    .tp_name="re.Match", .tp_basicsize=offsetof(MatchObject,caps), .tp_itemsize=sizeof(Py_ssize_t),
    .tp_dealloc=(destructor)match_dealloc, .tp_repr=(reprfunc)match_repr, .tp_flags=Py_TPFLAGS_DEFAULT, .tp_doc="Native regular expression match.",
    .tp_methods=MatchMethods, .tp_getset=MatchGetSet, .tp_as_mapping=&MatchMapping
};

static int fast_index(PyObject *value, Py_ssize_t *result) {
    PyObject *index=PyNumber_Index(value);
    if (!index) return 0;
    *result=PyLong_AsSsize_t(index);
    Py_DECREF(index);
    return !PyErr_Occurred();
}

static int pattern_window(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargsf, PyObject *kwnames, Subject *subject, Py_ssize_t *pos, Py_ssize_t *endpos) {
    Py_ssize_t nargs=PyVectorcall_NARGS(nargsf),nkeys=kwnames ? PyTuple_GET_SIZE(kwnames) : 0;
    if (nargs>3 || nkeys>3) { PyErr_SetString(PyExc_TypeError,"expected string and optional pos/endpos"); return 0; }
    PyObject *string=nargs>0 ? args[0] : NULL,*pos_value=nargs>1 ? args[1] : NULL,*end_value=nargs>2 ? args[2] : NULL;
    for (Py_ssize_t i=0; i<nkeys; i++) {
        PyObject *key=PyTuple_GET_ITEM(kwnames,i),*value=args[nargs+i];
        if (PyUnicode_CompareWithASCIIString(key,"string")==0 && !string) string=value;
        else if (PyUnicode_CompareWithASCIIString(key,"pos")==0 && !pos_value) pos_value=value;
        else if (PyUnicode_CompareWithASCIIString(key,"endpos")==0 && !end_value) end_value=value;
        else { PyErr_SetString(PyExc_TypeError,"invalid or repeated keyword argument"); return 0; }
    }
    if (!string) { PyErr_SetString(PyExc_TypeError,"missing required argument 'string'"); return 0; }
    *pos=0;
    if (pos_value && !fast_index(pos_value,pos)) return 0;
    if (!pattern_subject(pattern,string,subject)) return 0;
    if (!end_value) *endpos=subject->length;
    else if (!fast_index(end_value,endpos)) return 0;
    if (*pos<0) *pos=0;
    if (*endpos<0) *endpos=0;
    if (*endpos>subject->length) *endpos=subject->length;
    return 1;
}

static PyObject *pattern_single(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames, int mode) {
    Subject subject;
    Py_ssize_t pos,endpos;
    if (!pattern_window(pattern,args,nargs,kwnames,&subject,&pos,&endpos)) return NULL;
    if (pos>endpos) Py_RETURN_NONE;
    Py_ssize_t local_caps[34];
    Py_ssize_t cap_count=2*(pattern->groups+1);
    Py_ssize_t *caps=cap_count<=34 ? local_caps : PyMem_Malloc((size_t)cap_count*sizeof(Py_ssize_t));
    if (!caps) return PyErr_NoMemory();
    Py_ssize_t found=-1,finish=-1;
    Py_ssize_t last=-1;
    int got=find_one(pattern->vm,&subject,pos,endpos,mode,0,caps,&last,&found,&finish);
    if (got<0) { if (caps!=local_caps) PyMem_Free(caps); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
    if (!got) { if (caps!=local_caps) PyMem_Free(caps); Py_RETURN_NONE; }
    MatchObject *match=match_alloc(pattern,subject.obj,pos,endpos);
    if (!match) { if (caps!=local_caps) PyMem_Free(caps); return NULL; }
    memcpy(match->caps,caps,(size_t)cap_count*sizeof(Py_ssize_t)); match->lastindex=last;
    if (caps!=local_caps) PyMem_Free(caps);
    return (PyObject *)match;
}

static PyObject *pattern_search(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_single(pattern,args,nargs,kwnames,0); }
static PyObject *pattern_match(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_single(pattern,args,nargs,kwnames,1); }
static PyObject *pattern_fullmatch(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_single(pattern,args,nargs,kwnames,2); }

static PyObject *pattern_collect(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargsf, PyObject *kwnames, int mode) {
    Subject subject;
    Py_ssize_t pos=0,endpos=0,limit=0;
    if (mode==0) {
        if (!pattern_window(pattern,args,nargsf,kwnames,&subject,&pos,&endpos)) return NULL;
    } else {
        Py_ssize_t nargs=PyVectorcall_NARGS(nargsf),nkeys=kwnames ? PyTuple_GET_SIZE(kwnames) : 0;
        if (nargs>2 || nkeys>2) { PyErr_SetString(PyExc_TypeError,"expected string and optional maxsplit"); return NULL; }
        PyObject *string=nargs>0 ? args[0] : NULL,*limit_value=nargs>1 ? args[1] : NULL;
        for (Py_ssize_t i=0; i<nkeys; i++) {
            PyObject *key=PyTuple_GET_ITEM(kwnames,i),*value=args[nargs+i];
            if (PyUnicode_CompareWithASCIIString(key,"string")==0 && !string) string=value;
            else if (PyUnicode_CompareWithASCIIString(key,"maxsplit")==0 && !limit_value) limit_value=value;
            else { PyErr_SetString(PyExc_TypeError,"invalid or repeated keyword argument"); return NULL; }
        }
        if (!string) { PyErr_SetString(PyExc_TypeError,"missing required argument 'string'"); return NULL; }
        if (limit_value && !fast_index(limit_value,&limit)) return NULL;
        if (!pattern_subject(pattern,string,&subject)) return NULL;
        endpos=subject.length;
    }
    return collect_core(pattern->vm,subject,pos,endpos,limit,mode);
}

static PyObject *pattern_findall(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_collect(pattern,args,nargs,kwnames,0); }
static PyObject *pattern_split(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_collect(pattern,args,nargs,kwnames,1); }

static void finditer_dealloc(FindIterObject *iterator) {
    if (iterator->has_view) PyBuffer_Release(&iterator->view);
    Py_XDECREF(iterator->pattern); Py_XDECREF(iterator->string); Py_TYPE(iterator)->tp_free((PyObject *)iterator);
}
static PyObject *finditer_iter(PyObject *iterator) { return Py_NewRef(iterator); }

static PyObject *finditer_next(FindIterObject *iterator) {
    if (iterator->done || iterator->cursor>iterator->endpos) return NULL;
    MatchObject *match=match_alloc(iterator->pattern,iterator->string,iterator->original_pos,iterator->endpos);
    if (!match) return NULL;
    Py_ssize_t found=-1,finish=-1;
    int got=find_one(iterator->pattern->vm,&iterator->subject,iterator->cursor,iterator->endpos,0,iterator->nonempty,match->caps,&match->lastindex,&found,&finish);
    if (got<0) { Py_DECREF(match); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
    if (!got) { Py_DECREF(match); iterator->done=1; return NULL; }
    if (found==finish) { iterator->cursor=found; iterator->nonempty=1; }
    else { iterator->cursor=finish; iterator->nonempty=0; }
    return (PyObject *)match;
}

static PyObject *scanner_search(FindIterObject *iterator, PyObject *ignored) {
    (void)ignored;
    PyObject *result=finditer_next(iterator);
    if (result || PyErr_Occurred()) return result;
    Py_RETURN_NONE;
}

static PyObject *scanner_match(FindIterObject *iterator, PyObject *ignored) {
    (void)ignored;
    if (iterator->done || iterator->cursor>iterator->endpos) Py_RETURN_NONE;
    MatchObject *match=match_alloc(iterator->pattern,iterator->string,iterator->original_pos,iterator->endpos);
    if (!match) return NULL;
    Py_ssize_t found=-1,finish=-1;
    int got=find_one(iterator->pattern->vm,&iterator->subject,iterator->cursor,iterator->endpos,1,iterator->nonempty,match->caps,&match->lastindex,&found,&finish);
    if (got<0) { Py_DECREF(match); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
    if (!got) { Py_DECREF(match); iterator->done=1; Py_RETURN_NONE; }
    if (found==finish) { iterator->cursor=found; iterator->nonempty=1; }
    else { iterator->cursor=finish; iterator->nonempty=0; }
    return (PyObject *)match;
}

static PyMethodDef ScannerMethods[]={
    {"search",(PyCFunction)scanner_search,METH_NOARGS,"Scan for the next match."},
    {"match",(PyCFunction)scanner_match,METH_NOARGS,"Match at the current scanner position."},
    {NULL,NULL,0,NULL}
};

static PyObject *scanner_get_pattern(FindIterObject *iterator, void *closure) { (void)closure; return Py_NewRef(iterator->pattern); }
static PyGetSetDef ScannerGetSet[]={
    {"pattern",(getter)scanner_get_pattern,NULL,"Compiled pattern.",NULL},
    {NULL,NULL,NULL,NULL,NULL}
};

static PyTypeObject ScannerType={
    PyVarObject_HEAD_INIT(NULL,0)
    .tp_name="candidates._vm_native._Scanner", .tp_basicsize=sizeof(FindIterObject), .tp_dealloc=(destructor)finditer_dealloc,
    .tp_flags=Py_TPFLAGS_DEFAULT, .tp_doc="Native compiled-pattern scanner.", .tp_methods=ScannerMethods, .tp_getset=ScannerGetSet
};

static PyTypeObject FindIterType={
    PyVarObject_HEAD_INIT(NULL,0)
    .tp_name="candidates._vm_native._FindIter", .tp_basicsize=sizeof(FindIterObject), .tp_dealloc=(destructor)finditer_dealloc,
    .tp_flags=Py_TPFLAGS_DEFAULT, .tp_doc="Native non-overlapping match iterator.", .tp_iter=finditer_iter, .tp_iternext=(iternextfunc)finditer_next
};

static PyObject *pattern_iterator(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames, PyTypeObject *type) {
    Subject subject;
    Py_ssize_t pos,endpos;
    if (!pattern_window(pattern,args,nargs,kwnames,&subject,&pos,&endpos)) return NULL;
    FindIterObject *iterator=PyObject_New(FindIterObject,type);
    if (!iterator) return NULL;
    iterator->pattern=pattern; Py_INCREF(pattern);
    iterator->string=subject.obj; Py_INCREF(subject.obj);
    iterator->subject=subject;
    iterator->has_view=0;
    if (subject.byte_mode && !PyBytes_Check(subject.obj)) {
        if (PyObject_GetBuffer(subject.obj,&iterator->view,PyBUF_SIMPLE)<0) { Py_DECREF(iterator); return NULL; }
        iterator->has_view=1;
    }
    iterator->cursor=pos; iterator->endpos=endpos; iterator->original_pos=pos;
    iterator->nonempty=0; iterator->done=pos>endpos;
    return (PyObject *)iterator;
}

static PyObject *pattern_finditer(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_iterator(pattern,args,nargs,kwnames,&FindIterType); }
static PyObject *pattern_scanner(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_iterator(pattern,args,nargs,kwnames,&ScannerType); }

static PyObject *substitute_text(PatternObject *pattern, const Subject *subject, PyObject *replacement, PyObject *template_parts, Py_ssize_t limit, int return_count) {
    PyUnicodeWriter *writer=PyUnicodeWriter_Create(subject->length);
    if (!writer) return NULL;
    Py_ssize_t local_caps[34],cap_count=2*(pattern->groups+1);
    Py_ssize_t *caps=cap_count<=34 ? local_caps : PyMem_Malloc((size_t)cap_count*sizeof(Py_ssize_t));
    if (!caps) { PyUnicodeWriter_Discard(writer); return PyErr_NoMemory(); }
    Py_ssize_t cursor=0,previous=0,replacements=0,piece_count=0;
    int nonempty=0;
    while (cursor<=subject->length && (!limit || replacements<limit)) {
        Py_ssize_t last=-1,found=-1,finish=-1;
        int got=find_one(pattern->vm,subject,cursor,subject->length,0,nonempty,caps,&last,&found,&finish);
        if (got<0) { if (caps!=local_caps) PyMem_Free(caps); PyUnicodeWriter_Discard(writer); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
        if (!got) break;
        if (PyUnicodeWriter_WriteSubstring(writer,subject->obj,previous,found)<0) { if (caps!=local_caps) PyMem_Free(caps); PyUnicodeWriter_Discard(writer); return NULL; }
        if (found>previous) piece_count++;
        if (template_parts) {
            Py_ssize_t pieces=PyTuple_GET_SIZE(template_parts);
            for (Py_ssize_t i=0; i<pieces; i++) {
                PyObject *part=PyTuple_GET_ITEM(template_parts,i);
                int written;
                if (PyLong_Check(part)) {
                    Py_ssize_t number=PyLong_AsSsize_t(part);
                    if (PyErr_Occurred()) { if (caps!=local_caps) PyMem_Free(caps); PyUnicodeWriter_Discard(writer); return NULL; }
                    written=caps[2*number]<0 ? 0 : PyUnicodeWriter_WriteSubstring(writer,subject->obj,caps[2*number],caps[2*number+1]);
                } else written=PyUnicodeWriter_WriteStr(writer,part);
                if (written<0) { if (caps!=local_caps) PyMem_Free(caps); PyUnicodeWriter_Discard(writer); return NULL; }
            }
        } else {
            MatchObject *match=match_alloc(pattern,subject->obj,0,subject->length);
            if (!match) { if (caps!=local_caps) PyMem_Free(caps); PyUnicodeWriter_Discard(writer); return NULL; }
            memcpy(match->caps,caps,(size_t)cap_count*sizeof(Py_ssize_t)); match->lastindex=last;
            PyObject *value=PyObject_CallOneArg(replacement,(PyObject *)match);
            Py_DECREF(match);
            if (!value) { if (caps!=local_caps) PyMem_Free(caps); PyUnicodeWriter_Discard(writer); return NULL; }
            if (!PyUnicode_Check(value)) {
                PyErr_Format(PyExc_TypeError,"sequence item %zd: expected str instance, %.200s found",piece_count,Py_TYPE(value)->tp_name);
                Py_DECREF(value); if (caps!=local_caps) PyMem_Free(caps); PyUnicodeWriter_Discard(writer); return NULL;
            }
            int written=PyUnicodeWriter_WriteStr(writer,value);
            Py_DECREF(value);
            if (written<0) { if (caps!=local_caps) PyMem_Free(caps); PyUnicodeWriter_Discard(writer); return NULL; }
        }
        replacements++; piece_count++; previous=finish;
        if (found==finish) { cursor=found; nonempty=1; }
        else { cursor=finish; nonempty=0; }
    }
    if (caps!=local_caps) PyMem_Free(caps);
    if (PyUnicodeWriter_WriteSubstring(writer,subject->obj,previous,subject->length)<0) { PyUnicodeWriter_Discard(writer); return NULL; }
    PyObject *joined=PyUnicodeWriter_Finish(writer);
    if (!joined) return NULL;
    if (!return_count) return joined;
    PyObject *result=Py_BuildValue("On",joined,replacements);
    Py_DECREF(joined);
    return result;
}

static PyObject *pattern_substitute(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargsf, PyObject *kwnames, int return_count) {
    Py_ssize_t nargs=PyVectorcall_NARGS(nargsf),nkeys=kwnames ? PyTuple_GET_SIZE(kwnames) : 0;
    if (nargs>3 || nkeys>3) { PyErr_SetString(PyExc_TypeError,"expected replacement, string, and optional count"); return NULL; }
    PyObject *replacement=nargs>0 ? args[0] : NULL,*string=nargs>1 ? args[1] : NULL,*limit_value=nargs>2 ? args[2] : NULL;
    Py_ssize_t limit=0;
    for (Py_ssize_t i=0; i<nkeys; i++) {
        PyObject *key=PyTuple_GET_ITEM(kwnames,i),*value=args[nargs+i];
        if (PyUnicode_CompareWithASCIIString(key,"repl")==0 && !replacement) replacement=value;
        else if (PyUnicode_CompareWithASCIIString(key,"string")==0 && !string) string=value;
        else if (PyUnicode_CompareWithASCIIString(key,"count")==0 && !limit_value) limit_value=value;
        else { PyErr_SetString(PyExc_TypeError,"invalid or repeated keyword argument"); return NULL; }
    }
    if (!replacement || !string) { PyErr_SetString(PyExc_TypeError,"missing required replacement or string argument"); return NULL; }
    if (limit_value && !fast_index(limit_value,&limit)) return NULL;
    Subject subject;
    if (!pattern_subject(pattern,string,&subject)) return NULL;
    int callable=PyCallable_Check(replacement);
    PyObject *template_parts=NULL;
    int template_byte_mode=0,literal_replacement=0;
    if (!callable) {
        PyObject *owned_key=NULL,*template_key=replacement;
        if (PyByteArray_Check(replacement) || PyMemoryView_Check(replacement)) {
            owned_key=PyBytes_FromObject(replacement);
            if (!owned_key) return NULL;
            template_key=owned_key;
        }
        if (PyObject_Hash(template_key)==-1 && PyErr_Occurred()) { Py_XDECREF(owned_key); return NULL; }
        template_byte_mode=PyBytes_Check(template_key);
        if (template_byte_mode) literal_replacement=memchr(PyBytes_AS_STRING(template_key),'\\',(size_t)PyBytes_GET_SIZE(template_key))==NULL;
        else if (PyUnicode_Check(template_key)) literal_replacement=PyUnicode_FindChar(template_key,'\\',0,PyUnicode_GET_LENGTH(template_key),1)<0;
        if (PyErr_Occurred()) { Py_XDECREF(owned_key); return NULL; }
        if (!template_compiler) { Py_XDECREF(owned_key); PyErr_SetString(PyExc_RuntimeError,"native template compiler is not configured"); return NULL; }
        template_parts=PyDict_GetItemWithError(pattern->templates,template_key);
        if (!template_parts && PyErr_Occurred()) { Py_XDECREF(owned_key); return NULL; }
        if (!template_parts) {
            PyObject *byte_mode=template_byte_mode ? Py_True : Py_False;
            template_parts=PyObject_CallFunctionObjArgs(template_compiler,template_key,(PyObject *)pattern,byte_mode,NULL);
            if (!template_parts) { Py_XDECREF(owned_key); return NULL; }
            if (PyDict_SetItem(pattern->templates,template_key,template_parts)<0) { Py_DECREF(template_parts); Py_XDECREF(owned_key); return NULL; }
            Py_DECREF(template_parts);
            template_parts=PyDict_GetItemWithError(pattern->templates,template_key);
            if (!template_parts) { Py_XDECREF(owned_key); return NULL; }
        }
        Py_XDECREF(owned_key);
    }
    if (!callable && template_byte_mode!=subject.byte_mode) {
        Py_ssize_t cap_count=2*(pattern->groups+1),local_caps[34];
        Py_ssize_t *caps=cap_count<=34 ? local_caps : PyMem_Malloc((size_t)cap_count*sizeof(Py_ssize_t));
        if (!caps) return PyErr_NoMemory();
        Py_ssize_t last=-1,found=-1,finish=-1;
        int got=limit<0 ? 0 : find_one(pattern->vm,&subject,0,subject.length,0,0,caps,&last,&found,&finish);
        if (got<0) { if (caps!=local_caps) PyMem_Free(caps); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
        if (!got) {
            if (caps!=local_caps) PyMem_Free(caps);
            PyObject *unchanged=subject_slice(&subject,0,subject.length);
            if (!unchanged || !return_count) return unchanged;
            PyObject *result=Py_BuildValue("On",unchanged,(Py_ssize_t)0);
            Py_DECREF(unchanged);
            return result;
        }
        PyObject *value=NULL;
        if (literal_replacement) value=Py_NewRef(replacement);
        else {
            MatchObject *match=match_alloc(pattern,string,0,subject.length);
            if (!match) { if (caps!=local_caps) PyMem_Free(caps); return NULL; }
            memcpy(match->caps,caps,(size_t)cap_count*sizeof(Py_ssize_t)); match->lastindex=last;
            value=match_expand(match,replacement);
            Py_DECREF(match);
        }
        if (caps!=local_caps) PyMem_Free(caps);
        if (!value) return NULL;
        PyErr_Format(PyExc_TypeError,"sequence item %zd: expected %s, %.200s found",found>0 ? (Py_ssize_t)1 : (Py_ssize_t)0,subject.byte_mode?"a bytes-like object":"str instance",Py_TYPE(value)->tp_name);
        Py_DECREF(value);
        return NULL;
    }
    if (!callable && !return_count && pattern->vm->literal && PyTuple_GET_SIZE(template_parts)==1) {
        PyObject *part=PyTuple_GET_ITEM(template_parts,0);
        if (!subject.byte_mode && PyUnicode_Check(part)) return PyUnicode_Replace(subject.obj,pattern->vm->literal,part,limit ? limit : -1);
    }
    if (!subject.byte_mode) return substitute_text(pattern,&subject,callable ? replacement : NULL,template_parts,limit,return_count);
    PyObject *pieces=PyList_New(0);
    if (!pieces) return NULL;
    Py_ssize_t cap_count=2*(pattern->groups+1);
    Py_ssize_t *caps=PyMem_Malloc((size_t)cap_count*sizeof(Py_ssize_t));
    if (!caps) { Py_DECREF(pieces); return PyErr_NoMemory(); }
    Py_ssize_t cursor=0,previous=0,replacements=0;
    int nonempty=0;
    while (cursor<=subject.length && (!limit || replacements<limit)) {
        Py_ssize_t last=-1,found=-1,finish=-1;
        int got=find_one(pattern->vm,&subject,cursor,subject.length,0,nonempty,caps,&last,&found,&finish);
        if (got<0) { PyMem_Free(caps); Py_DECREF(pieces); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
        if (!got) break;
        if (found>previous) {
            PyObject *prefix=subject_slice(&subject,previous,found);
            if (!prefix || PyList_Append(pieces,prefix)<0) { Py_XDECREF(prefix); PyMem_Free(caps); Py_DECREF(pieces); return NULL; }
            Py_DECREF(prefix);
        }
        if (callable) {
            MatchObject *match=match_alloc(pattern,string,0,subject.length);
            if (!match) { PyMem_Free(caps); Py_DECREF(pieces); return NULL; }
            memcpy(match->caps,caps,(size_t)cap_count*sizeof(Py_ssize_t)); match->lastindex=last;
            PyObject *value=PyObject_CallOneArg(replacement,(PyObject *)match);
            Py_DECREF(match);
            if (!value) { PyMem_Free(caps); Py_DECREF(pieces); return NULL; }
            if (PyList_Append(pieces,value)<0) { Py_DECREF(value); PyMem_Free(caps); Py_DECREF(pieces); return NULL; }
            Py_DECREF(value);
        } else {
            Py_ssize_t count=PyTuple_GET_SIZE(template_parts);
            for (Py_ssize_t i=0; i<count; i++) {
                PyObject *part=PyTuple_GET_ITEM(template_parts,i),*value=NULL;
                if (PyLong_Check(part)) {
                    Py_ssize_t number=PyLong_AsSsize_t(part);
                    if (PyErr_Occurred()) { PyMem_Free(caps); Py_DECREF(pieces); return NULL; }
                    value=caps[2*number]<0 ? subject_slice(&subject,0,0) : subject_slice(&subject,caps[2*number],caps[2*number+1]);
                } else value=Py_NewRef(part);
                if (!value || PyList_Append(pieces,value)<0) { Py_XDECREF(value); PyMem_Free(caps); Py_DECREF(pieces); return NULL; }
                Py_DECREF(value);
            }
        }
        replacements++; previous=finish;
        if (found==finish) { cursor=found; nonempty=1; }
        else { cursor=finish; nonempty=0; }
    }
    PyMem_Free(caps);
    if (subject.length>previous) {
        PyObject *tail=subject_slice(&subject,previous,subject.length);
        if (!tail || PyList_Append(pieces,tail)<0) { Py_XDECREF(tail); Py_DECREF(pieces); return NULL; }
        Py_DECREF(tail);
    }
    PyObject *empty=subject_slice(&subject,0,0);
    if (!empty) { Py_DECREF(pieces); return NULL; }
    PyObject *joined=subject.byte_mode ? PyObject_CallMethod(empty,"join","O",pieces) : PyUnicode_Join(empty,pieces);
    Py_DECREF(empty); Py_DECREF(pieces);
    if (!joined) return NULL;
    if (!return_count) return joined;
    PyObject *result=Py_BuildValue("On",joined,replacements);
    Py_DECREF(joined);
    return result;
}

static PyObject *pattern_sub(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_substitute(pattern,args,nargs,kwnames,0); }
static PyObject *pattern_subn(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_substitute(pattern,args,nargs,kwnames,1); }

static int pattern_init(PatternObject *pattern, PyObject *args, PyObject *kwargs) {
    (void)kwargs;
    PyObject *value,*capsule,*groupindex;
    Py_ssize_t flags,groups;
    if (!PyArg_ParseTuple(args,"OnOnO",&value,&flags,&capsule,&groups,&groupindex)) return -1;
    VM *vm=PyCapsule_GetPointer(capsule,"rebar.vm");
    if (!vm) return -1;
    Py_XSETREF(pattern->pattern,Py_NewRef(value));
    Py_XSETREF(pattern->capsule,Py_NewRef(capsule));
    Py_XSETREF(pattern->groupindex,Py_NewRef(groupindex));
    Py_XSETREF(pattern->templates,PyDict_New());
    if (!pattern->templates) return -1;
    pattern->vm=vm; pattern->flags=flags; pattern->groups=groups;
    return 0;
}

static void pattern_dealloc(PatternObject *pattern) { Py_XDECREF(pattern->pattern); Py_XDECREF(pattern->groupindex); Py_XDECREF(pattern->capsule); Py_XDECREF(pattern->templates); Py_TYPE(pattern)->tp_free((PyObject *)pattern); }
static PyObject *pattern_get_pattern(PatternObject *pattern, void *closure) { (void)closure; return Py_NewRef(pattern->pattern); }
static PyObject *pattern_get_flags(PatternObject *pattern, void *closure) { (void)closure; return PyLong_FromSsize_t(pattern->flags); }
static PyObject *pattern_get_groups(PatternObject *pattern, void *closure) { (void)closure; return PyLong_FromSsize_t(pattern->groups); }
static PyObject *pattern_get_groupindex(PatternObject *pattern, void *closure) { (void)closure; return PyDictProxy_New(pattern->groupindex); }
static PyObject *pattern_get_vm(PatternObject *pattern, void *closure) { (void)closure; return Py_NewRef(pattern->capsule); }

static PyMethodDef PatternMethods[]={
    {"search",(PyCFunction)(void(*)(void))pattern_search,METH_FASTCALL|METH_KEYWORDS,"Scan for a match."},
    {"match",(PyCFunction)(void(*)(void))pattern_match,METH_FASTCALL|METH_KEYWORDS,"Match at the start."},
    {"fullmatch",(PyCFunction)(void(*)(void))pattern_fullmatch,METH_FASTCALL|METH_KEYWORDS,"Match the complete window."},
    {"findall",(PyCFunction)(void(*)(void))pattern_findall,METH_FASTCALL|METH_KEYWORDS,"Return all non-overlapping matches."},
    {"finditer",(PyCFunction)(void(*)(void))pattern_finditer,METH_FASTCALL|METH_KEYWORDS,"Iterate over non-overlapping matches."},
    {"scanner",(PyCFunction)(void(*)(void))pattern_scanner,METH_FASTCALL|METH_KEYWORDS,"Create a native pattern scanner."},
    {"split",(PyCFunction)(void(*)(void))pattern_split,METH_FASTCALL|METH_KEYWORDS,"Split around non-overlapping matches."},
    {"sub",(PyCFunction)(void(*)(void))pattern_sub,METH_FASTCALL|METH_KEYWORDS,"Replace non-overlapping matches."},
    {"subn",(PyCFunction)(void(*)(void))pattern_subn,METH_FASTCALL|METH_KEYWORDS,"Replace non-overlapping matches and return the count."},
    {NULL,NULL,0,NULL}
};

static PyGetSetDef PatternGetSet[]={
    {"pattern",(getter)pattern_get_pattern,NULL,"Original pattern.",NULL},{"flags",(getter)pattern_get_flags,NULL,"Pattern flags.",NULL},
    {"groups",(getter)pattern_get_groups,NULL,"Number of capture groups.",NULL},{"groupindex",(getter)pattern_get_groupindex,NULL,"Named group indexes.",NULL},
    {"_vm",(getter)pattern_get_vm,NULL,"Native bytecode program.",NULL},{NULL,NULL,NULL,NULL,NULL}
};

static PyTypeObject PatternType={
    PyVarObject_HEAD_INIT(NULL,0)
    .tp_name="candidates._vm_native._Pattern", .tp_basicsize=sizeof(PatternObject), .tp_dealloc=(destructor)pattern_dealloc,
    .tp_flags=Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, .tp_doc="Native compiled regular expression.", .tp_methods=PatternMethods,
    .tp_getset=PatternGetSet, .tp_init=(initproc)pattern_init, .tp_new=PyType_GenericNew
};

static PyObject *native_configure(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *expander,*compiler;
    if (!PyArg_ParseTuple(args,"OO",&expander,&compiler)) return NULL;
    if (!PyCallable_Check(expander) || !PyCallable_Check(compiler)) { PyErr_SetString(PyExc_TypeError,"template helpers must be callable"); return NULL; }
    Py_XSETREF(template_function,Py_NewRef(expander));
    Py_XSETREF(template_compiler,Py_NewRef(compiler));
    Py_RETURN_NONE;
}

static int escape_character(Py_UCS4 value) {
    switch (value) {
        case '(': case ')': case '[': case ']': case '{': case '}': case '?': case '*': case '+': case '-': case '|': case '^': case '$': case '\\': case '.': case '&': case '~': case '#': case ' ': case '\t': case '\n': case '\r': case '\v': case '\f': return 1;
        default: return 0;
    }
}

static PyObject *native_escape(PyObject *self, PyObject *value) {
    (void)self;
    if (PyUnicode_Check(value)) {
        Py_ssize_t length=PyUnicode_GET_LENGTH(value),extra=0;
        int source_kind=PyUnicode_KIND(value);
        const void *source=PyUnicode_DATA(value);
        for (Py_ssize_t index=0; index<length; index++) extra+=escape_character(PyUnicode_READ(source_kind,source,index));
        PyObject *result=PyUnicode_New(length+extra,PyUnicode_MAX_CHAR_VALUE(value));
        if (!result) return NULL;
        int target_kind=PyUnicode_KIND(result);
        void *target=PyUnicode_DATA(result);
        Py_ssize_t cursor=0;
        for (Py_ssize_t index=0; index<length; index++) {
            Py_UCS4 item=PyUnicode_READ(source_kind,source,index);
            if (escape_character(item)) PyUnicode_WRITE(target_kind,target,cursor++,'\\');
            PyUnicode_WRITE(target_kind,target,cursor++,item);
        }
        return result;
    }
    Py_buffer view;
    if (PyObject_GetBuffer(value,&view,PyBUF_SIMPLE)<0) {
        PyErr_Clear();
        PyErr_Format(PyExc_TypeError,"decoding to str: need a bytes-like object, %.200s found",Py_TYPE(value)->tp_name);
        return NULL;
    }
    const unsigned char *source=(const unsigned char *)view.buf;
    Py_ssize_t extra=0;
    for (Py_ssize_t index=0; index<view.len; index++) extra+=escape_character(source[index]);
    PyObject *result=PyBytes_FromStringAndSize(NULL,view.len+extra);
    if (!result) { PyBuffer_Release(&view); return NULL; }
    unsigned char *target=(unsigned char *)PyBytes_AS_STRING(result);
    Py_ssize_t cursor=0;
    for (Py_ssize_t index=0; index<view.len; index++) {
        unsigned char item=source[index];
        if (escape_character(item)) target[cursor++]='\\';
        target[cursor++]=item;
    }
    PyBuffer_Release(&view);
    return result;
}

static PyObject *native_profile(PyObject *self, PyObject *args) {
    (void)self;
    int reset=0;
    if (!PyArg_ParseTuple(args,"|p",&reset)) return NULL;
#ifdef REBAR_VM_PROFILE
    static const char *names[PROFILE_COUNT]={"find_calls","starts","start_rejected","pair_rejected","execute_calls","linear_calls","compact_calls","general_calls","state_new","state_clone","look_calls","class_checks","repeat_chars","steps"};
    PyObject *result=PyDict_New();
    if (!result) return NULL;
    for (int index=0; index<PROFILE_COUNT; index++) {
        PyObject *value=PyLong_FromUnsignedLongLong((unsigned long long)profile_counts[index]);
        if (!value || PyDict_SetItemString(result,names[index],value)<0) { Py_XDECREF(value); Py_DECREF(result); return NULL; }
        Py_DECREF(value);
    }
    if (reset) memset(profile_counts,0,sizeof(profile_counts));
    return result;
#else
    (void)reset;
    PyErr_SetString(PyExc_RuntimeError,"native VM was not built with REBAR_VM_PROFILE");
    return NULL;
#endif
}

static PyMethodDef Methods[]={{"build",native_build,METH_VARARGS,"Build a native bytecode program."},{"match",native_match,METH_VARARGS,"Execute a native bytecode program."},{"collect",native_collect,METH_VARARGS,"Collect non-overlapping native matches."},{"configure",native_configure,METH_VARARGS,"Configure native public helpers."},{"escape",native_escape,METH_O,"Escape regular-expression metacharacters."},{"profile",native_profile,METH_VARARGS,"Read optional native VM profile counters."},{NULL,NULL,0,NULL}};
static struct PyModuleDef Module={PyModuleDef_HEAD_INIT,"_vm_native","From-scratch bytecode regex VM.",-1,Methods,NULL,NULL,NULL,NULL};
PyMODINIT_FUNC PyInit__vm_native(void) {
    if (PyType_Ready(&PatternType)<0 || PyType_Ready(&MatchType)<0 || PyType_Ready(&FindIterType)<0 || PyType_Ready(&ScannerType)<0) return NULL;
    PyObject *module=PyModule_Create(&Module);
    if (!module) return NULL;
    if (PyModule_AddObjectRef(module,"Pattern",(PyObject *)&PatternType)<0 || PyModule_AddObjectRef(module,"Match",(PyObject *)&MatchType)<0) { Py_DECREF(module); return NULL; }
    return module;
}
