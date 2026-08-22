from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .models import Apparel, Purchase, PurchaseItem, Size


class AdminProductFlowTests(TestCase):
	def setUp(self):
		self.admin = User.objects.create_user(
			username="admin@example.com", password="strong-admin-password", is_staff=True
		)
		self.apparel = Apparel.objects.create(
			name="Original name",
			description="Original description",
			price="100.00",
			stock=3,
			main_image=SimpleUploadedFile("item.jpg", b"image-data", content_type="image/jpeg"),
		)
		self.size = Size.objects.get(code="M")

	def test_staff_login_opens_admin_product_index(self):
		response = self.client.post(
			"/login/",
			{"identifier": "admin@example.com", "password": "strong-admin-password", "next": "/cart/"},
		)

		self.assertRedirects(response, "/manage/")

	def test_staff_is_redirected_from_customer_urls(self):
		self.client.force_login(self.admin)

		for url in ("/", "/cart/", "/orders/", "/login/", "/signup/"):
			with self.subTest(url=url):
				response = self.client.get(url)
				self.assertRedirects(response, "/manage/")

	def test_staff_can_edit_product_and_save_all_fields(self):
		self.client.force_login(self.admin)
		response = self.client.post(
			f"/manage/products/apparel/{self.apparel.pk}/edit/",
			{
				"name": "Updated name",
				"description": "Updated description",
				"price": "125.00",
				"stock": "8",
				"is_active": "on",
				"sizes": [self.size.pk],
			},
		)

		self.assertRedirects(response, "/manage/")
		self.apparel.refresh_from_db()
		self.assertEqual(self.apparel.name, "Updated name")
		self.assertEqual(self.apparel.stock, 8)
		self.assertEqual(list(self.apparel.sizes.values_list("code", flat=True)), ["M"])


class OrderStatusFlowTests(TestCase):
	def setUp(self):
		self.customer = User.objects.create_user(
			username="customer@example.com", password="strong-customer-password"
		)
		self.other_customer = User.objects.create_user(
			username="other@example.com", password="strong-other-password"
		)
		self.admin = User.objects.create_user(
			username="orders-admin", password="strong-admin-password", is_staff=True
		)
		self.purchase = Purchase.objects.create(
			user=self.customer,
			customer_name="Customer",
			customer_email=self.customer.email,
			total="100.00",
		)
		PurchaseItem.objects.create(
			purchase=self.purchase,
			product_type="apparel",
			product_id=1,
			product_name="Test apparel",
			unit_price="100.00",
			quantity=1,
		)

	def test_customer_sees_only_own_orders_and_can_cancel_pending_order(self):
		other_purchase = Purchase.objects.create(
			user=self.other_customer,
			customer_name="Other customer",
			customer_email=self.other_customer.email,
			total="50.00",
		)
		self.client.force_login(self.customer)

		response = self.client.get("/orders/")
		self.assertContains(response, "Order #1")
		self.assertNotContains(response, f"Order #{other_purchase.pk}")

		response = self.client.post(f"/orders/{self.purchase.pk}/cancel/")
		self.assertRedirects(response, "/orders/")
		self.purchase.refresh_from_db()
		self.assertEqual(self.purchase.status, "cancelled")

	def test_customer_cannot_cancel_another_customers_order(self):
		self.client.force_login(self.other_customer)

		response = self.client.post(f"/orders/{self.purchase.pk}/cancel/")

		self.assertEqual(response.status_code, 404)
		self.purchase.refresh_from_db()
		self.assertEqual(self.purchase.status, "pending")

	def test_admin_can_assign_allowed_status_but_not_cancelled(self):
		self.client.force_login(self.admin)

		response = self.client.post(
			f"/manage/orders/{self.purchase.pk}/status/", {"status": "confirmed"}
		)
		self.assertRedirects(response, "/manage/orders/")
		self.purchase.refresh_from_db()
		self.assertEqual(self.purchase.status, "confirmed")

		self.client.post(
			f"/manage/orders/{self.purchase.pk}/status/", {"status": "cancelled"}
		)
		self.purchase.refresh_from_db()
		self.assertEqual(self.purchase.status, "confirmed")

# Create your tests here.
