#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stddef.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum { OP_CHAR=1, OP_DOT, OP_CAT, OP_CLASS, OP_ANCHOR, OP_BOUNDARY, OP_BACKREF,
       OP_SAVE_START, OP_SAVE_END, OP_SPLIT, OP_JUMP, OP_LOOK, OP_ATOMIC_START,
       OP_ATOMIC_END, OP_COND, OP_MATCH, OP_REPEAT1 };
enum { F_I=2, F_L=4, F_M=8, F_S=16, F_A=256, F_BYTE=1<<20 };

typedef struct { int op; Py_ssize_t a, b, c; } Ins;
typedef struct { Py_ssize_t count, atomic_capacity; int linear, compact; Ins *ins; } Code;
typedef struct { int kind; Py_UCS4 a, b; } ClassItem;
typedef struct { Py_ssize_t count; ClassItem *items; } CharClass;
typedef struct { Py_ssize_t code_count, class_count, groups; Code *codes; CharClass *classes; PyObject *literal; } VM;
typedef struct { PyObject *obj; int byte_mode; Py_ssize_t length; } Subject;
typedef struct { Py_ssize_t pc, pos, last, repeat_step, repeat_limit; Py_ssize_t *caps, *seen, *barrier; int atomic_depth; } State;
typedef struct { State **items; Py_ssize_t length, capacity; } Stack;

static void state_free(State *s) {
    if (!s) return;
    PyMem_Free(s);
}

static State *state_new(Py_ssize_t groups, const Code *code, Py_ssize_t pos,
                        const Py_ssize_t *caps, Py_ssize_t last) {
    Py_ssize_t cap_count = 2 * (groups + 1);
    State *s = PyMem_Malloc(sizeof(State) + (size_t)(cap_count + code->count + code->atomic_capacity) * sizeof(Py_ssize_t));
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
    if (s->byte_mode) return (unsigned char)PyBytes_AS_STRING(s->obj)[pos];
    return PyUnicode_READ_CHAR(s->obj, pos);
}

static Py_UCS4 folded(Py_UCS4 c, int ascii_only) {
    if (ascii_only) return c < 128 ? (c >= 'A' && c <= 'Z' ? c + 32 : c) : c;
    if (c == 0x130 || c == 0x131) return 'i';
    if (c == 0x17f) return 's';
    if (c == 0x212a) return 'k';
    return Py_UNICODE_TOLOWER(c);
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

static int class_match(const VM *vm, Py_ssize_t index, Py_UCS4 c, Py_ssize_t flags, int negate) {
    if (index < 0 || index >= vm->class_count) return 0;
    CharClass cls = vm->classes[index];
    int found = 0;
    int ascii_only = !!(flags & (F_A|F_L|F_BYTE));
    for (Py_ssize_t i=0; i<cls.count && !found; i++) {
        ClassItem item = cls.items[i];
        if (item.kind == 1) found = equal_char(item.a, c, flags);
        else if (item.kind == 2) {
            found = c >= item.a && c <= item.b;
            if (!found && (flags & F_I)) {
                Py_UCS4 fc = folded(c, ascii_only), fa = folded(item.a, ascii_only), fb = folded(item.b, ascii_only);
                found = fc >= fa && fc <= fb;
            }
        } else if (item.kind == 3) found = category(c, item.a, flags);
    }
    return negate ? !found : found;
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

static int repeat_needs_choice_inner(const VM *vm, const Code *code, Py_ssize_t next_pc, Ins atom, int depth) {
    if (depth>32) return 1;
    while (next_pc<code->count && (code->ins[next_pc].op==OP_SAVE_START || code->ins[next_pc].op==OP_SAVE_END)) next_pc++;
    if (next_pc>=code->count || code->ins[next_pc].op==OP_MATCH) return 0;
    Ins next=code->ins[next_pc];
    if (next.op==OP_JUMP) return repeat_needs_choice_inner(vm,code,next.a,atom,depth+1);
    if (next.op==OP_SPLIT) return repeat_needs_choice_inner(vm,code,next.a,atom,depth+1) || repeat_needs_choice_inner(vm,code,next.b,atom,depth+1);
    if (next.op==OP_ANCHOR && (next.a=='$' || next.a=='Z')) return 0;
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
    Py_ssize_t pos=start;
    for (Py_ssize_t pc=0; pc<code->count; pc++) {
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
                Py_ssize_t matched=0;
                while (matched<maximum && atom_match(vm,subject,pos+matched,atom)) matched++;
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

static int execute_compact_path(const VM *vm, const Code *code, const Subject *subject,
                                Py_ssize_t pc, Py_ssize_t pos, Py_ssize_t start,
                                Py_ssize_t endpos, Py_ssize_t *caps, Py_ssize_t *last,
                                Py_ssize_t *out_pos, int require_end,
                                int require_nonempty, int depth) {
    if (depth>128) return -2;
    Py_ssize_t cap_count=2*(vm->groups+1);
    while (pc>=0 && pc<code->count) {
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
                Py_ssize_t matched=0;
                while (matched<maximum && atom_match(vm,subject,pos+matched,atom)) matched++;
                if (matched<in.a) return 0;
                Py_ssize_t minimum_pos=pos+in.a,maximum_pos=pos+matched;
                pc+=2;
                if (in.c==2 || (in.c==0 && !repeat_needs_choice(vm,code,pc,atom))) { pos=maximum_pos; break; }
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
                   int require_nonempty, int depth) {
    if (depth > 128 || code_index < 0 || code_index >= vm->code_count) return -2;
    const Code *code = &vm->codes[code_index];
    if (code->linear) return execute_linear(vm,code_index,subject,start,endpos,caps,last,out_pos,require_end,require_nonempty);
    if (code->compact && vm->groups<=16) {
        int got=execute_compact_path(vm,code,subject,0,start,start,endpos,caps,last,out_pos,require_end,require_nonempty,0);
        if (got!=-2) return got;
    }
    Stack stack = {0};
    State *current = state_new(vm->groups, code, start, caps, *last);
    if (!current) return -1;
    for (;;) {
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
                Py_ssize_t matched=0;
                while (matched<maximum && atom_match(vm,subject,begin+matched,atom)) matched++;
                if (matched<in.a) goto fail;
                Py_ssize_t minimum=begin+in.a,furthest=begin+matched;
                current->pc+=2;
                if (in.c==1) current->pos=minimum;
                else current->pos=furthest;
                if (in.c!=2 && furthest>minimum && (in.c==1 || repeat_needs_choice(vm,code,current->pc,atom))) {
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
    for (Py_ssize_t i=0; i<vm->code_count; i++) PyMem_Free(vm->codes[i].ins);
    for (Py_ssize_t i=0; i<vm->class_count; i++) PyMem_Free(vm->classes[i].items);
    Py_XDECREF(vm->literal);
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
    for (Py_ssize_t p=0; p<vm->code_count; p++) {
        Code *code=&vm->codes[p];
        int deterministic=1;
        int compact=1;
        for (Py_ssize_t i=0; i<code->count; i++) {
            Ins in=code->ins[i];
            if (in.op==OP_SPLIT || in.op==OP_JUMP || in.op==OP_ATOMIC_START || in.op==OP_ATOMIC_END || in.op==OP_COND) deterministic=0;
            if (in.op==OP_LOOK && (in.a<0 || in.a>=vm->code_count || !vm->codes[in.a].linear)) deterministic=0;
            if (in.op==OP_SPLIT && in.c>=0) {
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
            if (in.op==OP_LOOK || in.op==OP_ATOMIC_START || in.op==OP_ATOMIC_END) compact=0;
            if (in.op==OP_REPEAT1) {
                if (i+1>=code->count || in.c==1 || repeat_needs_choice(vm,code,i+2,code->ins[i+1])) deterministic=0;
                i++;
            }
        }
        if (deterministic) code->linear=1;
        code->compact=compact;
    }
    if (vm->code_count && vm->codes[0].count>1) {
        Code main=vm->codes[0];
        Py_ssize_t length=main.count-1;
        int plain=main.ins[main.count-1].op==OP_MATCH,byte_mode=0;
        Py_UCS4 maximum=0;
        for (Py_ssize_t i=0; i<length && plain; i++) {
            Ins in=main.ins[i];
            if (in.op!=OP_CHAR || (in.b & F_I)) plain=0;
            else { if (in.b & F_BYTE) byte_mode=1; if ((Py_UCS4)in.a>maximum) maximum=(Py_UCS4)in.a; }
        }
        if (plain && length) {
            if (byte_mode) {
                vm->literal=PyBytes_FromStringAndSize(NULL,length);
                if (!vm->literal) goto error;
                char *data=PyBytes_AS_STRING(vm->literal);
                for (Py_ssize_t i=0; i<length; i++) data[i]=(char)main.ins[i].a;
            } else {
                vm->literal=PyUnicode_New(length,maximum);
                if (!vm->literal) goto error;
                int kind=PyUnicode_KIND(vm->literal); void *data=PyUnicode_DATA(vm->literal);
                for (Py_ssize_t i=0; i<length; i++) PyUnicode_WRITE(kind,data,i,(Py_UCS4)main.ins[i].a);
            }
        }
    }
    Py_DECREF(pseq); Py_DECREF(cseq);
    return PyCapsule_New(vm,"rebar.vm",capsule_free);
error:
    vm_free(vm); Py_DECREF(pseq); Py_DECREF(cseq); return NULL;
}

static int find_one(const VM *vm, const Subject *subject, Py_ssize_t pos,
                    Py_ssize_t endpos, int mode, int require_nonempty,
                    Py_ssize_t *caps, Py_ssize_t *last, Py_ssize_t *found,
                    Py_ssize_t *finish) {
    if (mode==0 && vm->literal) {
        Py_ssize_t length=subject->byte_mode ? PyBytes_GET_SIZE(vm->literal) : PyUnicode_GET_LENGTH(vm->literal);
        Py_ssize_t start=-1;
        if (subject->byte_mode) {
            const char *hay=PyBytes_AS_STRING(subject->obj),*needle=PyBytes_AS_STRING(vm->literal);
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
    if (mode==0 && !vm->groups && vm->code_count && vm->codes[0].count>3) {
        Code main=vm->codes[0];
        Py_ssize_t repeat_pc=0;
        while (repeat_pc<main.count && main.ins[repeat_pc].op==OP_SAVE_START) repeat_pc++;
        if (repeat_pc+2<main.count && main.ins[repeat_pc].op==OP_REPEAT1 && main.ins[repeat_pc].a>0 && main.ins[repeat_pc].c==0) {
            Ins repeat=main.ins[repeat_pc],atom=main.ins[repeat_pc+1];
            Py_ssize_t delimiter_pc=repeat_pc+2;
            while (delimiter_pc<main.count && main.ins[delimiter_pc].op==OP_SAVE_END) delimiter_pc++;
            if (delimiter_pc<main.count && main.ins[delimiter_pc].op==OP_CHAR && !atom_accepts(vm,atom,(Py_UCS4)main.ins[delimiter_pc].a)) {
                Ins delimiter=main.ins[delimiter_pc];
                Py_ssize_t cursor=pos+repeat.a;
                while (cursor<endpos) {
                    Py_ssize_t pivot=-1;
                    if (subject->byte_mode) {
                        const char *data=PyBytes_AS_STRING(subject->obj),*found_byte=memchr(data+cursor,(unsigned char)delimiter.a,(size_t)(endpos-cursor));
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
    if (mode==0 && vm->code_count && vm->codes[0].count>=2) {
        Code main = vm->codes[0];
        Py_ssize_t width = 0;
        int fixed = 1;
        for (Py_ssize_t pc=0; pc<main.count-1; pc++) {
            int op = main.ins[pc].op;
            if (op==OP_CHAR || op==OP_CLASS || op==OP_CAT || op==OP_DOT) width++;
            else if (op==OP_ANCHOR && pc==main.count-2 && main.ins[pc].a!='$') continue;
            else if (op==OP_ANCHOR && pc==main.count-2 && main.ins[pc].a=='$' && !(main.ins[pc].b & F_M)) continue;
            else { fixed=0; break; }
        }
        if (fixed && main.ins[main.count-2].op==OP_ANCHOR && main.ins[main.count-2].a=='$' && !(main.ins[main.count-2].b & F_M)) {
            first_start = endpos-width;
            last_start = first_start;
        }
    }
    for (Py_ssize_t start=first_start; start<=last_start; start++) {
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
            if (first.op==OP_CHAR && !equal_char(value,(Py_UCS4)first.a,first.b)) continue;
            if (first.op==OP_CLASS && !class_match(vm,first.a,value,first.b,(int)first.c)) continue;
            if (first.op==OP_CAT && !category(value,first.a,first.b)) continue;
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
    subject->obj=string; subject->byte_mode=PyBytes_Check(string); subject->length=0;
    if (subject->byte_mode) subject->length=PyBytes_GET_SIZE(string);
    else if (PyUnicode_Check(string)) subject->length=PyUnicode_GET_LENGTH(string);
    else { PyErr_SetString(PyExc_TypeError,"subject must be str or bytes"); return 0; }
    return 1;
}

static PyObject *subject_slice(const Subject *subject, Py_ssize_t begin, Py_ssize_t end) {
    if (subject->byte_mode) return PyBytes_FromStringAndSize(PyBytes_AS_STRING(subject->obj)+begin,end-begin);
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
} FindIterObject;

static PyTypeObject PatternType;
static PyTypeObject MatchType;
static PyTypeObject FindIterType;
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
    if (!PyLong_Check(value)) { PyErr_SetString(PyExc_IndexError,"no such group"); return 0; }
    *number=PyLong_AsSsize_t(value);
    if (PyErr_Occurred()) return 0;
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
    if (!template_function) { PyErr_SetString(PyExc_RuntimeError,"native template function is not configured"); return NULL; }
    return PyObject_CallFunctionObjArgs(template_function,template,(PyObject *)match,NULL);
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
    .tp_name="candidates._vm_native.Match", .tp_basicsize=offsetof(MatchObject,caps), .tp_itemsize=sizeof(Py_ssize_t),
    .tp_dealloc=(destructor)match_dealloc, .tp_flags=Py_TPFLAGS_DEFAULT, .tp_doc="Native regular expression match.",
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
    if (nargs<1 || nargs>3) { PyErr_SetString(PyExc_TypeError,"expected string and optional pos/endpos"); return 0; }
    PyObject *string=args[0],*pos_value=nargs>1 ? args[1] : NULL,*end_value=nargs>2 ? args[2] : Py_None;
    for (Py_ssize_t i=0; i<nkeys; i++) {
        PyObject *key=PyTuple_GET_ITEM(kwnames,i),*value=args[nargs+i];
        if (PyUnicode_CompareWithASCIIString(key,"pos")==0 && !pos_value) pos_value=value;
        else if (PyUnicode_CompareWithASCIIString(key,"endpos")==0 && end_value==Py_None) end_value=value;
        else { PyErr_SetString(PyExc_TypeError,"invalid or repeated keyword argument"); return 0; }
    }
    *pos=0;
    if (pos_value && !fast_index(pos_value,pos)) return 0;
    if (!pattern_subject(pattern,string,subject)) return 0;
    if (end_value==Py_None) *endpos=subject->length;
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
        if (nargs<1 || nargs>2 || nkeys>1) { PyErr_SetString(PyExc_TypeError,"expected string and optional maxsplit"); return NULL; }
        PyObject *string=args[0],*limit_value=nargs>1 ? args[1] : NULL;
        if (nkeys) {
            if (limit_value || PyUnicode_CompareWithASCIIString(PyTuple_GET_ITEM(kwnames,0),"maxsplit")!=0) { PyErr_SetString(PyExc_TypeError,"invalid or repeated keyword argument"); return NULL; }
            limit_value=args[nargs];
        }
        if (limit_value && !fast_index(limit_value,&limit)) return NULL;
        if (!pattern_subject(pattern,string,&subject)) return NULL;
        endpos=subject.length;
    }
    return collect_core(pattern->vm,subject,pos,endpos,limit,mode);
}

static PyObject *pattern_findall(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_collect(pattern,args,nargs,kwnames,0); }
static PyObject *pattern_split(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) { return pattern_collect(pattern,args,nargs,kwnames,1); }

static void finditer_dealloc(FindIterObject *iterator) { Py_XDECREF(iterator->pattern); Py_XDECREF(iterator->string); Py_TYPE(iterator)->tp_free((PyObject *)iterator); }
static PyObject *finditer_iter(PyObject *iterator) { return Py_NewRef(iterator); }

static PyObject *finditer_next(FindIterObject *iterator) {
    if (iterator->done || iterator->cursor>iterator->endpos) return NULL;
    Subject subject;
    if (!pattern_subject(iterator->pattern,iterator->string,&subject)) return NULL;
    MatchObject *match=match_alloc(iterator->pattern,iterator->string,iterator->original_pos,iterator->endpos);
    if (!match) return NULL;
    Py_ssize_t found=-1,finish=-1;
    int got=find_one(iterator->pattern->vm,&subject,iterator->cursor,iterator->endpos,0,iterator->nonempty,match->caps,&match->lastindex,&found,&finish);
    if (got<0) { Py_DECREF(match); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
    if (!got) { Py_DECREF(match); iterator->done=1; return NULL; }
    if (found==finish) { iterator->cursor=found; iterator->nonempty=1; }
    else { iterator->cursor=finish; iterator->nonempty=0; }
    return (PyObject *)match;
}

static PyTypeObject FindIterType={
    PyVarObject_HEAD_INIT(NULL,0)
    .tp_name="candidates._vm_native._FindIter", .tp_basicsize=sizeof(FindIterObject), .tp_dealloc=(destructor)finditer_dealloc,
    .tp_flags=Py_TPFLAGS_DEFAULT, .tp_doc="Native non-overlapping match iterator.", .tp_iter=finditer_iter, .tp_iternext=(iternextfunc)finditer_next
};

static PyObject *pattern_finditer(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargs, PyObject *kwnames) {
    Subject subject;
    Py_ssize_t pos,endpos;
    if (!pattern_window(pattern,args,nargs,kwnames,&subject,&pos,&endpos)) return NULL;
    FindIterObject *iterator=PyObject_New(FindIterObject,&FindIterType);
    if (!iterator) return NULL;
    iterator->pattern=pattern; Py_INCREF(pattern);
    iterator->string=subject.obj; Py_INCREF(subject.obj);
    iterator->cursor=pos; iterator->endpos=endpos; iterator->original_pos=pos;
    iterator->nonempty=0; iterator->done=pos>endpos;
    return (PyObject *)iterator;
}

static PyObject *pattern_substitute(PatternObject *pattern, PyObject *const *args, Py_ssize_t nargsf, PyObject *kwnames, int return_count) {
    Py_ssize_t nargs=PyVectorcall_NARGS(nargsf),nkeys=kwnames ? PyTuple_GET_SIZE(kwnames) : 0;
    if (nargs<2 || nargs>3 || nkeys>1) { PyErr_SetString(PyExc_TypeError,"expected replacement, string, and optional count"); return NULL; }
    PyObject *replacement=args[0],*string=args[1],*limit_value=nargs>2 ? args[2] : NULL;
    Py_ssize_t limit=0;
    if (nkeys) {
        if (limit_value || PyUnicode_CompareWithASCIIString(PyTuple_GET_ITEM(kwnames,0),"count")!=0) { PyErr_SetString(PyExc_TypeError,"invalid or repeated keyword argument"); return NULL; }
        limit_value=args[nargs];
    }
    if (limit_value && !fast_index(limit_value,&limit)) return NULL;
    Subject subject;
    if (!pattern_subject(pattern,string,&subject)) return NULL;
    int callable=PyCallable_Check(replacement);
    PyObject *template_parts=NULL;
    if (!callable) {
        if (!template_compiler) { PyErr_SetString(PyExc_RuntimeError,"native template compiler is not configured"); return NULL; }
        template_parts=PyDict_GetItemWithError(pattern->templates,replacement);
        if (!template_parts && PyErr_Occurred()) return NULL;
        if (!template_parts) {
            PyObject *byte_mode=subject.byte_mode ? Py_True : Py_False;
            template_parts=PyObject_CallFunctionObjArgs(template_compiler,replacement,(PyObject *)pattern,byte_mode,NULL);
            if (!template_parts) return NULL;
            if (PyDict_SetItem(pattern->templates,replacement,template_parts)<0) { Py_DECREF(template_parts); return NULL; }
            Py_DECREF(template_parts);
            template_parts=PyDict_GetItemWithError(pattern->templates,replacement);
            if (!template_parts) return NULL;
        }
    }
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
        PyObject *prefix=subject_slice(&subject,previous,found);
        if (!prefix || PyList_Append(pieces,prefix)<0) { Py_XDECREF(prefix); PyMem_Free(caps); Py_DECREF(pieces); return NULL; }
        Py_DECREF(prefix);
        if (callable) {
            MatchObject *match=match_alloc(pattern,string,0,subject.length);
            if (!match) { PyMem_Free(caps); Py_DECREF(pieces); return NULL; }
            memcpy(match->caps,caps,(size_t)cap_count*sizeof(Py_ssize_t)); match->lastindex=last;
            PyObject *value=PyObject_CallOneArg(replacement,(PyObject *)match);
            Py_DECREF(match);
            if (!value) { PyMem_Free(caps); Py_DECREF(pieces); return NULL; }
            int valid=subject.byte_mode ? PyBytes_Check(value) : PyUnicode_Check(value);
            if (!valid) {
                PyErr_Format(PyExc_TypeError,"sequence item %zd: expected a %s, %.200s found",PyList_GET_SIZE(pieces),subject.byte_mode?"bytes-like object":"str instance",Py_TYPE(value)->tp_name);
                Py_DECREF(value); PyMem_Free(caps); Py_DECREF(pieces); return NULL;
            }
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
    PyObject *tail=subject_slice(&subject,previous,subject.length);
    if (!tail || PyList_Append(pieces,tail)<0) { Py_XDECREF(tail); Py_DECREF(pieces); return NULL; }
    Py_DECREF(tail);
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
static PyObject *pattern_get_groupindex(PatternObject *pattern, void *closure) { (void)closure; return Py_NewRef(pattern->groupindex); }
static PyObject *pattern_get_vm(PatternObject *pattern, void *closure) { (void)closure; return Py_NewRef(pattern->capsule); }

static PyMethodDef PatternMethods[]={
    {"search",(PyCFunction)(void(*)(void))pattern_search,METH_FASTCALL|METH_KEYWORDS,"Scan for a match."},
    {"match",(PyCFunction)(void(*)(void))pattern_match,METH_FASTCALL|METH_KEYWORDS,"Match at the start."},
    {"fullmatch",(PyCFunction)(void(*)(void))pattern_fullmatch,METH_FASTCALL|METH_KEYWORDS,"Match the complete window."},
    {"findall",(PyCFunction)(void(*)(void))pattern_findall,METH_FASTCALL|METH_KEYWORDS,"Return all non-overlapping matches."},
    {"finditer",(PyCFunction)(void(*)(void))pattern_finditer,METH_FASTCALL|METH_KEYWORDS,"Iterate over non-overlapping matches."},
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

static PyMethodDef Methods[]={{"build",native_build,METH_VARARGS,"Build a native bytecode program."},{"match",native_match,METH_VARARGS,"Execute a native bytecode program."},{"collect",native_collect,METH_VARARGS,"Collect non-overlapping native matches."},{"configure",native_configure,METH_VARARGS,"Configure native public helpers."},{NULL,NULL,0,NULL}};
static struct PyModuleDef Module={PyModuleDef_HEAD_INIT,"_vm_native","From-scratch bytecode regex VM.",-1,Methods,NULL,NULL,NULL,NULL};
PyMODINIT_FUNC PyInit__vm_native(void) {
    if (PyType_Ready(&PatternType)<0 || PyType_Ready(&MatchType)<0 || PyType_Ready(&FindIterType)<0) return NULL;
    PyObject *module=PyModule_Create(&Module);
    if (!module) return NULL;
    if (PyModule_AddObjectRef(module,"Pattern",(PyObject *)&PatternType)<0 || PyModule_AddObjectRef(module,"Match",(PyObject *)&MatchType)<0) { Py_DECREF(module); return NULL; }
    return module;
}
