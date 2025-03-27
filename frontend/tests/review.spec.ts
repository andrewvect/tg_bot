import { test, expect } from '@playwright/test'

const dummyWords = [
	{ word_id: 1, word: 'test1', translation: 'trans1' },
	{ word_id: 2, word: 'test2', translation: 'trans2' }
]

test.beforeEach(async ({ page }) => {
	await page.addInitScript(() => {
		localStorage.setItem('token', 'dummy-token')
		;(window as any).__forceSetLoadingFalse = true
	})
})

test('displays loading spinner then content', async ({ page }) => {
	// Intercept review words count and words endpoints for one word
	await page.route('**/api/v1/cards/review/count', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: "1"
		})
	})
	await page.route('**/api/v1/cards/review/', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify({ words: [dummyWords[0]] })
		})
	})
	await page.goto('http://localhost:5173/review')
	// Expect card header (with dummyWords[0].word) to become visible eventually
	await expect(page.locator('text=' + dummyWords[0].word)).toBeVisible()
})

test('shows congratulatory message when no words available', async ({ page }) => {
	// Intercept endpoints to simulate no available words
	await page.route('**/api/v1/cards/review/count', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: "0"
		})
	})
	await page.route('**/api/v1/cards/review', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify({ words: [] })
		})
	})
	await page.goto('http://localhost:5173/review')
	await expect(page.locator('text=Все слова повторены!')).toBeVisible()
})

test('handles review action on card', async ({ page }) => {
	// Intercept endpoints so we have two words and catch addReview API calls
	await page.route('**/api/v1/cards/review/count', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: "2"
		})
	})

	await page.route('**/api/v1/cards/review/', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify({ words: dummyWords })
		})
	})
	await page.goto('http://localhost:5173/review')
	// Wait for first card with dummyWords[0]
	await expect(page.locator('text=' + dummyWords[0].word)).toBeVisible()
	// Click the view button (the first button; it reveals the translation)
	await page.locator('button').nth(0).click()
	await expect(page.locator('text=' + dummyWords[0].translation)).toBeVisible()
	// Click the check button (assumed to be the second button) to submit review action
	await page.locator('button').nth(1).click()
	// Now, the next card (dummyWords[1]) should be visible
	await expect(page.locator('text=' + dummyWords[1].word)).toBeVisible()
    await page.locator('button').nth(1).click()
    // The congratulatory message should be visible now
    await expect(page.locator('text=Все слова повторены!')).toBeVisible()
})
