# Comparison between PIT and Check0

From the file compareValidationMethods, we can see that the using PIT is requiring much less communication and computations. The prover using PIT validation uses 1323 vole indexes, but with Check0, it uses 3457 indexes.

# Backlog

Implement public values (possibly with scalar_mul)

Complete readme with instructions as to how this is implemented and works

Make expected polynomial public using field. (uses less communication and multiplication)

Instead of opening 27 values, use Schwartz-Zippel and PIT again.

Rewrite documentation where it is necessary.

Use higher securiry parameter.

Decouple wire commitment?