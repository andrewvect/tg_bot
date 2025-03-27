import { expect, test } from "@playwright/test"

test("User can toggle display settings radio buttons", async ({ page }) => {
  // Set token for authenticated requests
  await page.addInitScript(() => {
    localStorage.setItem('token', 'TEST_TOKEN')
  })

  // Intercept API call for user settings and return a fake response

  await page.goto("/settings")
  // Wait for the radio button corresponding to value "2" ("Русское") to be checked
  const serbianRadio = page.getByRole("radio", { name: "Сербское" })
  await expect(serbianRadio).toBeChecked()

  // Change selection to "Сербское" (value "1")
  const russianRadio = page.getByRole("radio", { name: "Русское" })
  // Instead of clicking the radio input, click its label to trigger a change in checked state
  const russianLabel = page.getByText("Русское")
  await russianLabel.click({ force: true })
  await expect(russianRadio).toBeChecked()

  // Change selection to "Рандомное" (value "3")
  const randomRadio = page.getByRole("radio", { name: "Рандомное" })
  const randomLabel = page.getByText("Рандомное")
  await randomLabel.click()
  await expect(randomRadio).toBeChecked()

  // Optionally, navigate back
  const backButton = page.getByRole("button", { name: "Назад" })

  await backButton.click()
  // Assert that the user was redirected to the home page
  await expect(page).toHaveURL("/main")
  // ...existing navigation assertions...
})
