/**
 * dsh-theme-anydoor — host half.
 *
 * Pure browser-side capability: the empty apply exists so the row appears in
 * the host cordis.yml / Loader (same pattern as
 * `@deepseek-ai/dsh-cordis-client-runner`). The browser half ships through
 * `exports["./client"]` and is discovered from the package.json `dsh.client`
 * declaration.
 */
function apply() {}

export { apply };
