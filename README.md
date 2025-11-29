# Comparison between PIT and Check0

From the file compareValidationMethods, we can see that the using PIT is requiring much less communication and computations. The prover using PIT validation uses 1323 vole indexes, but with Check0, it uses 3457 indexes.

# Backlog

Implement public values in the sudoku, such that the verifier knows it is the right sudoku which has been commited to (possibly with scalar_mul)

Complete readme with instructions as to how this is implemented and works

Instead of opening 27 values, use Schwartz-Zippel and PIT again.

Use higher security parameter.