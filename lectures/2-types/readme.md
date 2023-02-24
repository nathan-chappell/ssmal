# Lecture 2: Types

## Overview

Practically speaking, a *type* is metadata associated to a variable or parameter in a program.
Proper use of *type annotations* and a *type checker* can help ensure program correctness.
Different *type systems* have different expressive power - some are even turing complete.
Some tools are capable of *type inference,* which can reduce tedious and error prone coding practices.
Some languages offer the ability to read, and even modify, information about types *at runtime.*  Such techniques are broadly called *reflection.*

* Examples...

TODO: come up with a "framework" for demonstrating the type systems I want to show...

## Simple Types

* definition, usage in python, checking, inference
* implicational fragment of predicate logic
* __WARNING: MATH__ Types as Trees

## Recursive Types

* definition, usage in python, checking, inference
* typing the Y-Combinator
* __WARNING: MATH__ Recursive-types as Trees, regular-languages

## Subtype-Polymorphism

### Nominal Subtyping

* inheritance + transitivity
* definition, usage in python, checking, inference

### Structural Subtyping

* *ducktyping*
* definition, usage in python, checking, inference

## Generalized Type Systems

Functions are of the `kind`: `value -> value`

Other `kinds` include:
* `value -> Type` - think of overloaded functions
* `Type -> Type` - think of generic containers
* `Type -> value` is less interesting, but we can encode computation into the type system...

### Ad-hoc Polymorphism

* `value -> Type`
* definition, usage in python, checking, inference
* overloads, dependent-types
* first-order logic

### Parametric Polymorphism

* `Type -> Type`
* definition, usage in python, checking, inference
* overloads, dependent-types
* second-order logic
* typing the Y-Combinator

# Assignment:

* Consider the following from **ECMA 335 (5th edition, December 2010) section 9.2**:

![ecma-335-9.2_1](./img/ecma-335-9.2_1.png)
![ecma-335-9.2_2](./img/ecma-335-9.2_2.png)

![ecma-335-9.2-example-1](./img/ecma-335-9.2-example-1.png)
![ecma-335-9.2-example-2](./img/ecma-335-9.2-example-2.png)
![ecma-335-9.2-example-3](./img/ecma-335-9.2-example-3.png)

## Your task:

<!-- TODO: come up with something to do -->