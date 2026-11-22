const { test, expect } = require('@playwright/test');

test('inicio carga el carrusel, navegación y buscador', async ({ page }) => {
  await page.goto('/');

  await expect(page).toHaveTitle(/Bienes Raíces Multicasa/);
  await expect(page.locator('#heroMainCarousel')).toBeVisible();
  await expect(page.locator('#heroMainCarousel .carousel-item')).toHaveCount(4);
  await expect(page.getByRole('heading', { name: 'BIENVENIDO' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'ENCUENTRA TU FUTURA PROPIEDAD' })).toBeVisible();
  await expect(page.locator('#compania')).toBeAttached();
  await expect(page.locator('#buscador')).toBeAttached();
});

test('busqueda publica conserva filtros y muestra resultados', async ({ page }) => {
  await page.goto('/?buscar=1&ciudad=Saltillo');

  await expect(page.locator('#buscador')).toBeAttached();
  await expect(page.locator('#resultados')).toBeAttached();
  await expect(page.locator('#id_ciudad')).toHaveValue('Saltillo');
});
