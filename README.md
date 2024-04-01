# python-gen

`python-gen` is a Python-library for automatic Python-code generation with support for the presence/absence of the specified [linter rules](https://docs.astral.sh/ruff/rules/).
This project is aimed at fuzzing-testing various Python-code analysis tools on generated programs with specified properties.  
(The project is currently under active development)

## How to run

* Install [`libcst`](https://pypi.org/project/libcst/)

```bash
pip install libcst
```

* Due to this project adds its own logic to the work of `libcst`, we have to crack the source code of library a little (this is true for versions 1.1.0, 1.2.0 and possibly others)

```bash
sed -i '117s/self._validate()/pass/' <path_to_libcst>/_nodes/base.py
```

* Run `generate.py` script from the root of this project

```bash
python3 generate.py <seed> [options...]
```

where `seed` is a number for random generator

## Structure of generated programs

* Generated program consists of several function definitions without parameters followed by a block of code.

* Block of code consists of simple assign statements and condition statements.

* Expression consists of numbers, variables and tuples.

## Options

The following options are available:

* `-unused_variable`, `-uv`, `-F481` -- generate code without `unused-variable`
* `-undefined_name`, `-un`, `-F421` -- generate code without `undefined-name`
* `+if_tuple`, `+it`, `+F634` -- generate code with `if-tuple`
* `-if_tuple`, `-it`, `-F634` -- generate code without `if-tuple`

## Example

```
$ python3 generate.py 54 +it -un -uv
def OlR38Tbf():
    Zb3593dZse = 1858
    jIoyGh7 = True
    v = True
    p = True
    if None:
        Wgg = (Zb3593dZse, None, 581, 35)
        t3eGY = 7279
        lzjVB4N5B = jIoyGh7
        mniQvzT = 8
        EN6_hS = (28,)
        KkyE8 = t3eGY
        a4K = False
        (Wgg, lzjVB4N5B, mniQvzT, EN6_hS, KkyE8, a4K)
    FXxz = True
    if 1811:
        l2E = 513
        (l2E,)
    bT3pdumWC = ()
    (v, p, FXxz, bT3pdumWC)
glXvwOGfbq = 861
if True:
    u = True
    OwzfJ = None
    hxT7eFZnCV = 75
    LIQQ1dAjyn = None
    if None:
        wQLkcyl = u
        lzBh7vU = False
        P498iy = 17
        OP = True
        cYw8eXsPaQ = 14933
        BW = None
        (wQLkcyl, lzBh7vU, P498iy, OP, cYw8eXsPaQ, BW)
    FuT6_9bK = hxT7eFZnCV
    k = hxT7eFZnCV
    (OwzfJ, LIQQ1dAjyn, FuT6_9bK, k)
grHg = None
maUpR = True
CTE = 484241
a = 0
RkxCNjsX_5 = maUpR
(OlR38Tbf, glXvwOGfbq, grHg, CTE, a, RkxCNjsX_5)
if (0,):
    pass

```

## Testing `ruff`

This project also allow to test [`ruff`](https://pypi.org/project/ruff/)

```bash
python3 main.py
```
