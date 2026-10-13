/**
 * SPA extraction cache freshness probe. Runs in a persistent Electron isolated
 * world, returns counters only; never serializes a mutation, DOM node or text.
 *
 * Playwright snapshotterInjected.ts's mutation observation is a reference
 * pattern (Apache-2.0). This is an independent Hermes implementation.
 */
export interface DomRevisionEvidence {
  revision: number
  generation: number
  cacheable: boolean
}

export function domRevisionProbeScript(): string {
  return `(function () {
    var root = document.documentElement;
    if (!root || typeof MutationObserver !== 'function') {
      return { revision: 0, generation: 0, cacheable: false };
    }
    var key = '__hermesExtractDomRevision';
    var current = window[key];
    if (!current || current.root !== root) {
      if (current && current.observer) current.observer.disconnect();
      var generation = (Number(window.__hermesExtractDomGeneration) || 0) + 1;
      window.__hermesExtractDomGeneration = generation;
      current = { root: root, generation: generation, revision: 0, observer: null };
      try {
        current.observer = new MutationObserver(function(changes) {
          if (changes.length) current.revision += 1;
        });
        current.observer.observe(root, {
          subtree: true, childList: true, characterData: true, attributes: true
        });
        window[key] = current;
      } catch (_) {
        return { revision: 0, generation: generation, cacheable: false };
      }
    }
    try {
      var pending = current.observer.takeRecords();
      if (pending.length) current.revision += 1;
      // MutationObserver does not observe internal Shadow DOM or frame DOM.
      // Rather than hand back a stale cached item, disable reuse for these.
      var all = document.getElementsByTagName('*');
      if (all.length > 2500) {
        return { revision: current.revision, generation: current.generation, cacheable: false };
      }
      for (var i = 0; i < all.length; i++) {
        if (all[i].shadowRoot || all[i].tagName === 'IFRAME' || all[i].tagName === 'FRAME') {
          return { revision: current.revision, generation: current.generation, cacheable: false };
        }
      }
      return { revision: current.revision, generation: current.generation, cacheable: true };
    } catch (_) {
      return { revision: 0, generation: 0, cacheable: false };
    }
  })()`
}

export function isSafeDomRevisionEvidence(value: unknown): value is DomRevisionEvidence {
  if (!value || typeof value !== 'object') {return false}
  const entry = value as Record<string, unknown>

  return (
    typeof entry.cacheable === 'boolean' &&
    Number.isSafeInteger(entry.revision) && (entry.revision as number) >= 0 &&
    Number.isSafeInteger(entry.generation) && (entry.generation as number) >= 1
  )
}
