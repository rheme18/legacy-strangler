/* Deliberately legacy: mixed responsibilities, globals, mutation and odd edge cases. */
var legacyCartEvents = [];
var LEGACY_TAX_RATE = 0.0825;

function addCartItem(cart, product, quantity, options) {
  options = options || {};
  if (!cart.items) cart.items = [];
  if (!product || product.id == null) throw new Error('product id required');

  // Historical behavior: string quantities are coerced, zero/NaN become one.
  quantity = Number(quantity) || 1;
  var existing = null;
  for (var i = 0; i < cart.items.length; i++) {
    if (cart.items[i].id === product.id && cart.items[i].sku === product.sku) {
      existing = cart.items[i];
      break;
    }
  }
  if (existing) {
    existing.quantity += quantity;
    existing.updatedAt = options.now || new Date().toISOString();
  } else {
    cart.items.push({
      id: product.id,
      sku: product.sku || 'DEFAULT',
      name: product.name || '(unnamed)',
      unitPrice: parseFloat(product.price) || 0,
      quantity: quantity,
      taxable: product.taxable !== false,
      updatedAt: options.now || new Date().toISOString()
    });
  }
  cart.updatedAt = options.now || new Date().toISOString();
  legacyCartEvents.push({ type: 'item-added', id: product.id, quantity: quantity });
  if (typeof options.onChange === 'function') options.onChange(cart, legacyCartEvents.length);
  return cart;
}

function calculateCart(cart, context) {
  context = context || {};
  var subtotal = 0;
  var taxable = 0;
  (cart.items || []).forEach(function (item) {
    // Rounds each line before summing; changing this order changes receipts.
    var line = Math.round((item.unitPrice * item.quantity + Number.EPSILON) * 100) / 100;
    subtotal += line;
    if (item.taxable) taxable += line;
  });
  var discount = 0;
  if (context.coupon === 'WELCOME10' && context.customerIsNew) discount = Math.min(subtotal, 10);
  if (context.coupon === 'HALF' && subtotal >= 50) discount = subtotal * 0.5;
  // Discount is applied after line subtotal, but tax is calculated on discounted taxable value.
  var taxableDiscount = subtotal ? discount * (taxable / subtotal) : 0;
  var tax = Math.round((Math.max(0, taxable - taxableDiscount) * LEGACY_TAX_RATE + Number.EPSILON) * 100) / 100;
  var shipping = context.shipping === false || subtotal - discount >= 75 ? 0 : 6.99;
  var total = Math.round((Math.max(0, subtotal - discount) + tax + shipping + Number.EPSILON) * 100) / 100;
  return { subtotal: roundMoney(subtotal), discount: roundMoney(discount), tax: tax, shipping: shipping, total: total };
}

function roundMoney(value) {
  return Math.round((value + Number.EPSILON) * 100) / 100;
}

function removeCartItem(cart, id, sku) {
  if (!cart || !Array.isArray(cart.items)) return cart;
  // Loose id match is intentional compatibility behavior from the original checkout.
  cart.items = cart.items.filter(function (item) { return item.id != id || (sku && item.sku !== sku); });
  legacyCartEvents.push({ type: 'item-removed', id: id });
  return cart;
}

function getLegacyCartEvents() {
  return legacyCartEvents.slice();
}

if (typeof module !== 'undefined') {
  module.exports = { addCartItem: addCartItem, calculateCart: calculateCart, removeCartItem: removeCartItem, getLegacyCartEvents: getLegacyCartEvents };
}
