import { AxeBuilder } from "@axe-core/playwright";
import { expect, test } from "@playwright/test";

import { mockDraftResponse } from "./fixtures/draftResponse";

test.beforeEach(async ({ page }) => {
  await page.route("**/v1/drafts", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(mockDraftResponse),
    });
  });
});

test("main workspace has no critical accessibility violations", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Load sample" }).click();
  await page.getByRole("button", { name: "Run draft" }).click();

  const results = await new AxeBuilder({ page }).analyze();
  const seriousViolations = results.violations.filter((violation) =>
    ["critical", "serious"].includes(violation.impact ?? ""),
  );

  expect(seriousViolations).toEqual([]);
});
