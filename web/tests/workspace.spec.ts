import { expect, test } from "@playwright/test";

import { mockDraftResponse } from "./fixtures/draftResponse";

test.beforeEach(async ({ page }) => {
  await page.route("**/v1/drafts", async (route) => {
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify(mockDraftResponse),
    });
  });
  await page.route("**/v1/reviews", async (route) => {
    const request = route.request().postDataJSON();
    await route.fulfill({
      contentType: "application/json",
      body: JSON.stringify({
        review: {
          draft_id: request.draft_id,
          item_key: request.item_key,
          decision: request.decision,
          reason_codes: request.reason_codes,
          comments: request.comments,
          edited_text: null,
          created_at: "2026-04-27T00:00:00Z",
        },
      }),
    });
  });
});

test("runs assignment sample and highlights evidence", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Load sample" }).click();
  await page.getByRole("button", { name: "Run draft" }).click();

  await expect(page.getByText("HbA1c increased from 7.8%")).toBeVisible();
  await expect(page.getByText("Fasting glucose recency is unclear")).toBeVisible();

  await page.getByRole("button", { name: "S3" }).first().click();
  await expect(page.getByRole("button", { name: /S3 Fasting glucose/ })).toBeVisible();
});

test("records frontend-only review decisions", async ({ page }) => {
  await page.goto("/");

  await page.getByRole("button", { name: "Load sample" }).click();
  await page.getByRole("button", { name: "Run draft" }).click();
  await page.getByRole("button", { name: "Accept" }).first().click();

  await expect(page.getByText("accept").first()).toBeVisible();
  await expect(page.getByText("saved").first()).toBeVisible();

  await page.getByRole("button", { name: "Wrong evidence" }).first().click();
  await expect(page.getByText("edit").first()).toBeVisible();
});

test("mobile layout keeps primary controls reachable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.getByRole("button", { name: "Load sample" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Safety panel" })).toBeVisible();
  await page.screenshot({ fullPage: true, path: "test-results/mobile-workspace.png" });
});
