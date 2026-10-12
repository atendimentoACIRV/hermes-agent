import type { BrowserBatchStep } from './workstation-browser-batch'

/**
 * Ephemeral, renderer-local readback. This is evidence for a step, never a
 * second execution, admission or receipt owner. Values must not be logged.
 */
export interface BatchObservation {
  url: string
  documentToken: string
  elementToken: number | null
  found: boolean
  editable: boolean
  value: string | null
  checked: boolean | null
  pressed: string | null
  expanded: string | null
  scrollY: number
}

export function batchObservationScript(ref: string | null): string {
  return `(function () {
    // __HERMES_BATCH_READBACK_V1__
    var state = window.__hermesWorkstationRefs;
    var el = state && state.byRef && state.byRef.get(${JSON.stringify(ref)});
    var found = !!(el && el.isConnected);
    var token = null;
    if (found && state) {
      if (!state.batchIdentityByElement) state.batchIdentityByElement = new WeakMap();
      if (!state.batchIdentityByElement.has(el)) {
        state.batchElementCounter = (state.batchElementCounter || 0) + 1;
        state.batchIdentityByElement.set(el, state.batchElementCounter);
      }
      token = state.batchIdentityByElement.get(el);
    }
    var tag = found ? String(el.tagName || '').toLowerCase() : '';
    var editable = found && (tag === 'input' || tag === 'textarea' || !!el.isContentEditable);
    var value = editable ? ('value' in el ? String(el.value) : String(el.textContent || '')) : null;
    return {
      url: location.href,
      documentToken: String(performance.timeOrigin),
      elementToken: typeof token === 'number' ? token : null,
      found: found,
      editable: !!editable,
      value: value,
      checked: found && typeof el.checked === 'boolean' ? el.checked : null,
      pressed: found ? el.getAttribute('aria-pressed') : null,
      expanded: found ? el.getAttribute('aria-expanded') : null,
      scrollY: window.scrollY
    };
  })()`
}

export function hasVerifiedBatchEffect(
  step: BrowserBatchStep,
  before: BatchObservation | null,
  after: BatchObservation | null
): { verified: boolean; reason: string } {
  const uncertain = (reason: string) => ({ verified: false, reason })
  if (!before || !after) return uncertain('readback_unavailable')
  if (
    !before.url ||
    before.url !== after.url ||
    !before.documentToken ||
    before.documentToken !== after.documentToken
  ) {
    return uncertain('document_changed')
  }
  if (step.kind === 'scroll') {
    if (!Number.isFinite(before.scrollY) || !Number.isFinite(after.scrollY)) return uncertain('scroll_not_observable')
    const delta = after.scrollY - before.scrollY
    return delta * (step.direction === 'down' ? 1 : -1) > 0
      ? { verified: true, reason: 'scroll_readback' }
      : uncertain('scroll_effect_not_observed')
  }
  if (!before.found || !after.found || before.elementToken === null || before.elementToken !== after.elementToken) {
    return uncertain('stale_or_replaced_target')
  }
  if (step.kind === 'type') {
    if (!before.editable || !after.editable || before.value === null || after.value === null) {
      return uncertain('input_readback_unavailable')
    }
    const append = step.append === true || step.clear === false
    const expected = append ? before.value + step.text : step.text
    return after.value === expected
      ? { verified: true, reason: 'input_value_readback' }
      : uncertain('input_value_mismatch')
  }
  if (step.kind === 'click') {
    const toggled =
      (before.checked !== null && after.checked !== null && before.checked !== after.checked) ||
      (before.pressed !== null && after.pressed !== null && before.pressed !== after.pressed) ||
      (before.expanded !== null && after.expanded !== null && before.expanded !== after.expanded)
    return toggled ? { verified: true, reason: 'toggle_readback' } : uncertain('click_postcondition_not_observed')
  }
  // A key dispatch is not proof that the website consumed the key.
  return uncertain('key_postcondition_not_observed')
}
