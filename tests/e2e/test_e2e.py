import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8000"

# ── credenciales de prueba ─────────────────────────────────────────────────────
TEST_USER = "testuser"
TEST_PASS = "testpass123"


def login(page: Page):
    """Registra (si no existe) e inicia sesión antes de cada test."""
    page.goto(BASE_URL)

    # Intentar registrar (puede fallar si ya existe, no importa)
    page.click('[data-tab="register"]')
    page.fill("#reg-username", TEST_USER)
    page.fill("#reg-password", TEST_PASS)
    page.click("#register-form button[type='submit']")
    page.wait_for_timeout(500)

    # Hacer login
    page.click('[data-tab="login"]')
    page.fill("#login-username", TEST_USER)
    page.fill("#login-password", TEST_PASS)
    page.click("#login-form button[type='submit']")

    # Esperar a que desaparezca el overlay
    page.wait_for_selector("#auth-overlay.hidden")


@pytest.fixture
def conversation_id(page: Page) -> int:
    login(page)
    page.click("#new-conv-btn")
    page.wait_for_selector(".conv-item")
    item = page.locator(".conv-item").first
    return int(item.get_attribute("data-id"))


def test_crear_conversacion(page: Page):
    login(page)
    page.click("#new-conv-btn")
    expect(page.locator(".conv-item")).to_be_visible()
    expect(page.locator("#prompt")).to_be_enabled()
    expect(page.locator("#send")).to_be_enabled()


def test_enviar_y_recibir_mensaje(page: Page, conversation_id: int):
    login(page)
    page.click(f'.conv-item[data-id="{conversation_id}"]')
    page.fill("#prompt", "Hola, ¿cómo estás?")
    page.click("#send")
    page.wait_for_selector(".message.user")
    expect(page.locator(".message.user .bubble")).to_contain_text("Hola")


def test_lista_conversaciones_persisted(page: Page, conversation_id: int):
    login(page)
    expect(page.locator(f'.conv-item[data-id="{conversation_id}"]')).to_be_visible()


def test_cambiar_entre_conversaciones(page: Page):
    login(page)
    page.click("#new-conv-btn")
    page.wait_for_timeout(200)
    page.click("#new-conv-btn")
    page.wait_for_timeout(200)
    items = page.locator(".conv-item")
    expect(items).to_have_count(2)