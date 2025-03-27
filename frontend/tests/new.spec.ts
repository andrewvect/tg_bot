import { test, expect } from '@playwright/test'

test.beforeEach(async ({ page }) => {
	// Initialize token using addInitScript so localStorage is properly set on page load
	await page.addInitScript(() => {
		localStorage.setItem('token', 'dummy-token')
		// Set global flag to force loading to false in tests
		;(window as any).__forceSetLoadingFalse = true
	})
})

test('displays loading spinner then content', async ({ page }) => {
	// Remove new_words before navigation using addInitScript
	await page.addInitScript(() => {
		localStorage.removeItem('new_words')
	})
	await page.goto('http://localhost:5173/new')
	// Expect loading spinner (first occurrence) to be visible
	await expect(page.locator('text=Loading...').first()).toBeVisible()
})

test('shows congratulatory message when no words available', async ({ page }) => {
	// Set empty new_words via addInitScript prior to navigation
	await page.addInitScript(() => {
		localStorage.setItem('new_words', JSON.stringify([]))
	})
	await page.goto('http://localhost:5173/new')
	// Expect congratulatory header to appear
	await expect(page.locator('text=Поздравляем!')).toBeVisible()
})

test('handles "Добавить" button for adding new card', async ({ page }) => {

	// Counter to count API calls made when pressing "Добавить"
	await page.addInitScript(() => {
		localStorage.setItem('token', 'TEST_TOKEN')
	  })

	let newCardCallCount = 0;

	const dummyWords = Array.from({ length: 10 }, (_, i) => ({
		  word_id: i + 1,
		  word: `word${i + 1}`,
		  translation: `translation${i + 1}`
	  }));

	  await page.route('**/api/v1/cards/', async (route) => {
		  await route.fulfill({
			  status: 200,
			  contentType: 'application/json',
			  body: JSON.stringify({ words: dummyWords })
		  });
	  });

	await page.goto('http://localhost:5173/new')

	// Click the "Добавить" button 10 times
	for (let i = 1; i < 10; i++) {
		await page.click('button:has-text("Добавить")')
		await expect(page.locator(`text=word${i + 1}`)).toBeVisible()
		await expect(page.locator(`text=translation${i + 1}`)).toBeVisible()

		// check that the API call was made to create new card
	}


})

test('handles "Уже знаю" button for adding new card', async ({ page }) => {

	// Counter to count API calls made when pressing "Добавить"
	await page.addInitScript(() => {
		localStorage.setItem('token', 'TEST_TOKEN')
	  })

	const dummyWords = Array.from({ length: 10 }, (_, i) => ({
		  word_id: i + 1,
		  word: `word${i + 1}`,
		  translation: `translation${i + 1}`
	  }));

	  await page.route('**/api/v1/cards/', async (route) => {
		  await route.fulfill({
			  status: 200,
			  contentType: 'application/json',
			  body: JSON.stringify({ words: dummyWords })
		  });
	  });

	await page.goto('http://localhost:5173/new')

	// Click the "Добавить" button 10 times
	for (let i = 1; i < 10; i++) {
		await page.click('button:has-text("Уже знаю")')
		await expect(page.locator(`text=word${i + 1}`)).toBeVisible()
		await expect(page.locator(`text=translation${i + 1}`)).toBeVisible()

		// check that the API call was made to create new card

	}
	// intercept tha Api call

	await page.click('button:has-text("Уже знаю")')

	await page.route('**/api/v1/cards/', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify([])
		});
	});

	// check there is 'Поздравляем!' message
	await expect(page.locator('text=Поздравляем!')).toBeVisible()




})
