#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

enum { OP_CHAR=1, OP_DOT, OP_CAT, OP_CLASS, OP_ANCHOR, OP_BOUNDARY, OP_BACKREF,
       OP_SAVE_START, OP_SAVE_END, OP_SPLIT, OP_JUMP, OP_LOOK, OP_ATOMIC_START,
       OP_ATOMIC_END, OP_COND, OP_MATCH };
enum { F_I=2, F_L=4, F_M=8, F_S=16, F_A=256, F_BYTE=1<<20 };

typedef struct { int op; Py_ssize_t a, b, c; } Ins;
typedef struct { Py_ssize_t count; Ins *ins; } Code;
typedef struct { int kind; Py_UCS4 a, b; } ClassItem;
typedef struct { Py_ssize_t count; ClassItem *items; } CharClass;
typedef struct { Py_ssize_t code_count, class_count, groups; Code *codes; CharClass *classes; } VM;
typedef struct { PyObject *obj; int byte_mode; Py_ssize_t length; } Subject;
typedef struct { Py_ssize_t pc, pos, last; Py_ssize_t *caps, *seen; int atomic_depth; Py_ssize_t barrier[32]; } State;
typedef struct { State **items; Py_ssize_t length, capacity; } Stack;

static void state_free(State *s) {
    if (!s) return;
    PyMem_Free(s->caps);
    PyMem_Free(s->seen);
    PyMem_Free(s);
}

static State *state_new(Py_ssize_t groups, Py_ssize_t code_len, Py_ssize_t pos,
                        const Py_ssize_t *caps, Py_ssize_t last) {
    State *s = PyMem_Calloc(1, sizeof(State));
    if (!s) return NULL;
    s->caps = PyMem_Malloc((size_t)(2 * (groups + 1)) * sizeof(Py_ssize_t));
    s->seen = PyMem_Malloc((size_t)code_len * sizeof(Py_ssize_t));
    if (!s->caps || !s->seen) { state_free(s); return NULL; }
    memcpy(s->caps, caps, (size_t)(2 * (groups + 1)) * sizeof(Py_ssize_t));
    for (Py_ssize_t i=0; i<code_len; i++) s->seen[i] = -1;
    s->pos = pos;
    s->last = last;
    return s;
}

static State *state_clone(const State *old, Py_ssize_t groups, Py_ssize_t code_len) {
    State *s = state_new(groups, code_len, old->pos, old->caps, old->last);
    if (!s) return NULL;
    s->pc = old->pc;
    s->atomic_depth = old->atomic_depth;
    memcpy(s->barrier, old->barrier, sizeof(old->barrier));
    memcpy(s->seen, old->seen, (size_t)code_len * sizeof(Py_ssize_t));
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

static int execute(const VM *vm, Py_ssize_t code_index, const Subject *subject,
                   Py_ssize_t start, Py_ssize_t endpos, Py_ssize_t *caps,
                   Py_ssize_t *last, Py_ssize_t *out_pos, int require_end,
                   int require_nonempty, int depth) {
    if (depth > 128 || code_index < 0 || code_index >= vm->code_count) return -2;
    const Code *code = &vm->codes[code_index];
    Stack stack = {0};
    State *current = state_new(vm->groups, code->count, start, caps, *last);
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
                State *alternate = state_clone(current,vm->groups,code->count);
                if (!alternate) { state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return -1; }
                alternate->pc = in.b;
                if (!stack_push(&stack,alternate)) { state_free(alternate); state_free(current); stack_trim(&stack,0); PyMem_Free(stack.items); return -1; }
                current->pc = in.a; break;
            }
            case OP_ATOMIC_START:
                if (current->atomic_depth >= 32) goto fail;
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
    }
}

static void vm_free(VM *vm) {
    if (!vm) return;
    for (Py_ssize_t i=0; i<vm->code_count; i++) PyMem_Free(vm->codes[i].ins);
    for (Py_ssize_t i=0; i<vm->class_count; i++) PyMem_Free(vm->classes[i].items);
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
    for (Py_ssize_t p=0; p<vm->code_count; p++) {
        PyObject *seq = PySequence_Fast(PySequence_Fast_GET_ITEM(pseq,p),"program must be a sequence");
        if (!seq) goto error;
        vm->codes[p].count=PySequence_Fast_GET_SIZE(seq); vm->codes[p].ins=PyMem_Calloc((size_t)vm->codes[p].count,sizeof(Ins));
        if (!vm->codes[p].ins) { Py_DECREF(seq); PyErr_NoMemory(); goto error; }
        for (Py_ssize_t i=0; i<vm->codes[p].count; i++) {
            PyObject *row=PySequence_Fast_GET_ITEM(seq,i);
            if (!PyArg_ParseTuple(row,"innn",&vm->codes[p].ins[i].op,&vm->codes[p].ins[i].a,&vm->codes[p].ins[i].b,&vm->codes[p].ins[i].c)) { Py_DECREF(seq); goto error; }
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
    Py_DECREF(pseq); Py_DECREF(cseq);
    return PyCapsule_New(vm,"rebar.vm",capsule_free);
error:
    vm_free(vm); Py_DECREF(pseq); Py_DECREF(cseq); return NULL;
}

static PyObject *native_match(PyObject *self, PyObject *args) {
    (void)self;
    PyObject *capsule,*string;
    Py_ssize_t pos,endpos;
    int mode,require_nonempty;
    if (!PyArg_ParseTuple(args,"OOnnii",&capsule,&string,&pos,&endpos,&mode,&require_nonempty)) return NULL;
    VM *vm=PyCapsule_GetPointer(capsule,"rebar.vm");
    if (!vm) return NULL;
    Subject subject={string,PyBytes_Check(string),0};
    if (subject.byte_mode) subject.length=PyBytes_GET_SIZE(string);
    else if (PyUnicode_Check(string)) subject.length=PyUnicode_GET_LENGTH(string);
    else { PyErr_SetString(PyExc_TypeError,"subject must be str or bytes"); return NULL; }
    if (pos<0) pos=0;
    if (endpos<0) endpos=0;
    if (endpos>subject.length) endpos=subject.length;
    if (pos>endpos) Py_RETURN_NONE;
    Py_ssize_t *caps=PyMem_Malloc((size_t)(2*(vm->groups+1))*sizeof(Py_ssize_t));
    if (!caps) return PyErr_NoMemory();
    for (Py_ssize_t start=pos; start<=endpos; start++) {
        for (Py_ssize_t i=0; i<2*(vm->groups+1); i++) caps[i]=-1;
        caps[0]=start;
        Py_ssize_t last=-1,finish=-1;
        int got=execute(vm,0,&subject,start,endpos,caps,&last,&finish,mode==2,require_nonempty && start==pos,0);
        if (got<0) { PyMem_Free(caps); PyErr_SetString(PyExc_RuntimeError,got==-1?"native VM allocation failed":"native VM recursion limit"); return NULL; }
        if (got) {
            caps[1]=finish;
            PyObject *spans=PyList_New(vm->groups+1);
            if (!spans) { PyMem_Free(caps); return NULL; }
            for (Py_ssize_t g=0; g<=vm->groups; g++) {
                PyObject *item;
                if (caps[2*g]<0) { item=Py_None; Py_INCREF(item); }
                else item=Py_BuildValue("(nn)",caps[2*g],caps[2*g+1]);
                if (!item) { Py_DECREF(spans); PyMem_Free(caps); return NULL; }
                PyList_SET_ITEM(spans,g,item);
            }
            PyObject *last_obj = last<0 ? Py_NewRef(Py_None) : PyLong_FromSsize_t(last);
            PyObject *result=Py_BuildValue("nnOO",start,finish,spans,last_obj);
            Py_DECREF(spans); Py_DECREF(last_obj); PyMem_Free(caps); return result;
        }
        if (mode!=0) break;
    }
    PyMem_Free(caps); Py_RETURN_NONE;
}

static PyMethodDef Methods[]={{"build",native_build,METH_VARARGS,"Build a native bytecode program."},{"match",native_match,METH_VARARGS,"Execute a native bytecode program."},{NULL,NULL,0,NULL}};
static struct PyModuleDef Module={PyModuleDef_HEAD_INIT,"_vm_native","From-scratch bytecode regex VM.",-1,Methods,NULL,NULL,NULL,NULL};
PyMODINIT_FUNC PyInit__vm_native(void) { return PyModule_Create(&Module); }
