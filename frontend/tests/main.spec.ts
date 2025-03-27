import { expect, test } from "@playwright/test"

test("User can toggle display settings radio buttons and see review count", async ({ page }) => {
  // Set token for authenticated requests
  await page.addInitScript(() => {
    localStorage.setItem('token', 'TEST_TOKEN')
  })

  // Navigate to main component
  await page.goto("/main")

  // ...wait for component load if necessary...
  await expect(page.locator('text=Добавить новые слова')).toBeVisible()
  await expect(page.locator('text=Повторить слова')).toBeVisible()
  await expect(page.locator('text=Настройки')).toBeVisible()
  await expect(page.locator('div.css-1x5d0a')).toHaveText("0")


})

test("Check words counter", async ({ page }) => {
  // Set token for authenticated requests
  await page.addInitScript(() => {
    localStorage.setItem('token', 'TEST_TOKEN')
  })

  // Intercept API call before navigation
  await page.route('**/api/v1/cards/review/count', route => {
    route.fulfill({
      status: 200,
      body: JSON.stringify({ count: 5 })
    })
  })

  // Navigate to main component
  await page.goto("/main")

  // ...wait for component load if necessary...
  await expect(page.locator('text=Добавить новые слова')).toBeVisible()
  await expect(page.locator('text=Повторить слова')).toBeVisible()
  await expect(page.locator('text=Настройки')).toBeVisible()
  await expect(page.locator('div.css-1x5d0a')).toHaveText("5")
})
