# JavaScript to TypeScript sample

This tiny fixture is intentionally messy so a migration agent has behavior to discover before it rewrites anything. It has shared mutable event state, in-place cart mutation, callback side effects, permissive coercion, loose ID matching, per-line rounding, coupon rules, tax allocation, and a free-shipping threshold.

From the repository root, run the mapper against this fixture:

```sh
python .agents/skills/legacy-strangler/scripts/dependency_mapper.py examples/js-to-ts-sample --format markdown
```

Try a prompt such as: “Use the `legacy-strangler` skill to migrate `legacy_cart.js` to TypeScript. First map dependencies, write characterization tests for current behavior, then add a side-by-side adapter. Do not remove the JavaScript file until parity is demonstrated.”

Suggested edge cases to characterize include string/zero/invalid quantities, missing product IDs, absent prices, duplicate IDs with different SKUs, empty carts, coupon thresholds, taxable versus non-taxable items, rounding boundaries, missing cart state, and callback/event ordering.
