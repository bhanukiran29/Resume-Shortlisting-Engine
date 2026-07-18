export function getSettingsSupport() {
  // TODO: Backend does not currently expose settings/configuration endpoints.
  return {
    supported: false,
    reason: "Settings API is not exposed by the current backend.",
  };
}
