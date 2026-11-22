const { test, expect } = require('@playwright/test');

test('inicio de sesion rechaza credenciales invalidas', async ({ page }) => {
  await page.goto('/login/');
  await page.getByLabel('Nombre de usuario').fill('usuario-inexistente');
  await page.getByLabel('Contraseña').fill('credencial-invalida');
  await page.getByRole('button', { name: 'Entrar' }).click();

  await expect(page).toHaveURL(/\/login\//);
  await expect(page.locator('.errorlist')).toBeVisible();
});

test('rutas administrativas redirigen usuarios anonimos', async ({ page }) => {
  await page.goto('/gestion/casas/');
  await expect(page).toHaveURL(/\/login\/\?next=\/gestion\/casas\//);

  await page.goto('/reportes/');
  await expect(page).toHaveURL(/\/login\/\?next=\/reportes\//);
});
