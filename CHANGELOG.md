# Changelog

- [v0.4.7](#v047)
- [v0.4.6](#v046)
- [v0.4.5](#v045)
- [v0.4.4](#v044)
- [v0.4.3](#v043)

## v0.4.7

Pretty big fixes, should make pfp a *lot* more compatible with existing
010 Editor templates (DEX.bt works now for parsing!)

| type | ticket                                               | description                                      |
|------|------------------------------------------------------|--------------------------------------------------|
| bug  | [#120](https://github.com/d0c-s4vage/pfp/issues/120) | Fixes integer promotion problems, part deux      |
| bug  | [#115](https://github.com/d0c-s4vage/pfp/issues/115) | Fixes problem with chained assignments           |
| bug  | [#113](https://github.com/d0c-s4vage/pfp/issues/113) | Error with `_pfp__parse` and `set_val` parameter |

## v0.4.6

Consecutive duplicate arrays are now fully supported

| type | ticket                                               | description                                   |
|-----:|------------------------------------------------------|-----------------------------------------------|
|  bug | [#110](https://github.com/d0c-s4vage/pfp/issues/110) | Adds support for consecutive duplicate arrays |

## v0.4.5

MP4.bt works now!

| type | ticket                                               | description        |
|-----:|------------------------------------------------------|--------------------|
|  bug | [#100](https://github.com/d0c-s4vage/pfp/issues/100) | Implemented Memcmp |

## v0.4.4

| type | ticket                                             | description                                        |
|-----:|----------------------------------------------------|----------------------------------------------------|
|  bug | [#98](https://github.com/d0c-s4vage/pfp/issues/98) | Fixes problem with typedef'd parameterized structs |

## v0.4.3

Vastly improves struct support/handling in pfp

| type | ticket                                             | description                                      |
|-----:|----------------------------------------------------|--------------------------------------------------|
|  bug | [#26](https://github.com/d0c-s4vage/pfp/issues/26) | Fixes many problems with struct support/handling |
