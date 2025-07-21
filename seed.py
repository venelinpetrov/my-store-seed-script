import mysql.connector
import random
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

class DatabaseSeeder:
    def __init__(self, host, user, password, database, clean_start=False):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.conn.cursor()
        self.clean_start = clean_start

        # Multi-country data
        self.countries = {
            'USA': ['California', 'New York', 'Texas', 'Florida', 'Illinois'],
            'Canada': ['Ontario', 'Quebec', 'British Columbia', 'Alberta', 'Manitoba'],
            'UK': ['England', 'Scotland', 'Wales', 'Northern Ireland'],
            'Germany': ['Bavaria', 'North Rhine-Westphalia', 'Baden-Württemberg', 'Lower Saxony'],
            'France': ['Île-de-France', 'Provence-Alpes-Côte d\'Azur', 'Occitanie', 'Hauts-de-France'],
            'Australia': ['New South Wales', 'Victoria', 'Queensland', 'Western Australia'],
            'Japan': ['Tokyo', 'Osaka', 'Kanagawa', 'Aichi', 'Saitama']
        }

        self.cities = {
            'USA': ['Los Angeles', 'New York', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego', 'Dallas', 'San Jose'],
            'Canada': ['Toronto', 'Montreal', 'Vancouver', 'Calgary', 'Edmonton', 'Ottawa', 'Winnipeg', 'Quebec City'],
            'UK': ['London', 'Birmingham', 'Manchester', 'Leeds', 'Liverpool', 'Sheffield', 'Bristol', 'Edinburgh'],
            'Germany': ['Berlin', 'Munich', 'Hamburg', 'Cologne', 'Frankfurt', 'Stuttgart', 'Düsseldorf', 'Dortmund'],
            'France': ['Paris', 'Lyon', 'Marseille', 'Toulouse', 'Nice', 'Nantes', 'Strasbourg', 'Montpellier'],
            'Australia': ['Sydney', 'Melbourne', 'Brisbane', 'Perth', 'Adelaide', 'Gold Coast', 'Newcastle', 'Canberra'],
            'Japan': ['Tokyo', 'Yokohama', 'Osaka', 'Nagoya', 'Sapporo', 'Fukuoka', 'Kobe', 'Kyoto']
        }

        self.first_names = [
            'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda', 'David', 'Elizabeth',
            'William', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica', 'Thomas', 'Sarah', 'Christopher', 'Karen',
            'Charles', 'Nancy', 'Daniel', 'Lisa', 'Matthew', 'Betty', 'Anthony', 'Helen', 'Mark', 'Sandra',
            'Emma', 'Liam', 'Olivia', 'Noah', 'Ava', 'Oliver', 'Isabella', 'Elijah', 'Sophia', 'Lucas',
            'Hiroshi', 'Yuki', 'Takeshi', 'Akiko', 'Hans', 'Greta', 'Pierre', 'Marie', 'Ahmed', 'Fatima'
        ]

        self.last_names = [
            'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
            'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
            'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
            'Tanaka', 'Sato', 'Suzuki', 'Takahashi', 'Watanabe', 'Müller', 'Schmidt', 'Schneider', 'Fischer', 'Meyer',
            'Dubois', 'Martin', 'Bernard', 'Thomas', 'Robert', 'Petit', 'Durand', 'Leroy', 'Moreau', 'Simon'
        ]

    def clean_database(self):
        """Clean all data from tables (useful for fresh start)"""
        tables_to_clean = [
            'payments', 'invoices', 'shipments', 'order_items', 'orders',
            'variant_option_assignments', 'product_variants', 'inventory_levels',
            'product_tags', 'product_to_categories', 'variant_option_values',
            'variant_options', 'products', 'tags', 'brands', 'product_categories',
            'customer_addresses', 'customers', 'payment_statuses', 'payment_methods',
            'order_statuses', 'address_types'
        ]

        # Disable foreign key checks temporarily
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        for table in tables_to_clean:
            try:
                self.cursor.execute(f"DELETE FROM {table}")
                self.cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1")
                print(f"Cleaned {table}")
            except mysql.connector.Error as e:
                print(f"Warning: Could not clean {table}: {e}")

        # Re-enable foreign key checks
        self.cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        self.conn.commit()
        print("Database cleaned successfully!")

    def generate_date_range(self, start_year=2022, end_year=2024):
        """Generate random date within range"""
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        return start_date + timedelta(days=random_days)

    def seed_address_types(self):
        """Seed address types"""
        address_types = ['Home', 'Work', 'Shipping', 'Billing']

        for addr_type in address_types:
            try:
                self.cursor.execute(
                    "INSERT INTO address_types (type_name) VALUES (%s)",
                    (addr_type,)
                )
            except mysql.connector.IntegrityError:
                pass  # Skip duplicates
        self.conn.commit()
        print("Seeded address_types")

    def seed_customers(self, count=500):
        """Seed customers with realistic data"""
        existing_emails = set()

        # Get existing emails to avoid duplicates
        self.cursor.execute("SELECT email FROM customers")
        for (email,) in self.cursor.fetchall():
            existing_emails.add(email)

        successful_inserts = 0
        attempts = 0
        max_attempts = count * 3  # Prevent infinite loop

        while successful_inserts < count and attempts < max_attempts:
            attempts += 1
            first_name = random.choice(self.first_names)
            last_name = random.choice(self.last_names)
            name = f"{first_name} {last_name}"

            # Generate unique email
            email_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
            email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{random.choice(email_domains)}"

            if email in existing_emails:
                continue

            # Generate phone numbers for different countries
            country_phones = {
                'USA': f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                'Canada': f"+1-{random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}",
                'UK': f"+44-{random.randint(1000, 9999)}-{random.randint(100000, 999999)}",
                'Germany': f"+49-{random.randint(30, 89)}-{random.randint(10000000, 99999999)}",
                'France': f"+33-{random.randint(1, 9)}-{random.randint(10000000, 99999999)}",
                'Australia': f"+61-{random.randint(2, 9)}-{random.randint(10000000, 99999999)}",
                'Japan': f"+81-{random.randint(3, 9)}-{random.randint(10000000, 99999999)}"
            }

            phone = random.choice(list(country_phones.values()))
            created_at = self.generate_date_range(2022, 2024)

            try:
                self.cursor.execute(
                    "INSERT INTO customers (name, email, phone, created_at) VALUES (%s, %s, %s, %s)",
                    (name, email, phone, created_at)
                )
                existing_emails.add(email)
                successful_inserts += 1
            except mysql.connector.IntegrityError:
                continue  # Try again with different data

        self.conn.commit()
        print(f"Seeded {successful_inserts} customers")

    def seed_customer_addresses(self):
        """Seed customer addresses"""
        self.cursor.execute("SELECT customer_id FROM customers")
        customer_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT address_type_id FROM address_types")
        address_type_ids = [row[0] for row in self.cursor.fetchall()]

        for customer_id in customer_ids:
            # Each customer gets 1-3 addresses
            num_addresses = random.randint(1, 3)

            for i in range(num_addresses):
                country = random.choice(list(self.countries.keys()))
                state = random.choice(self.countries[country])
                city = random.choice(self.cities[country])
                street = f"{random.randint(1, 9999)} {random.choice(['Main St', 'Oak Ave', 'Park Rd', 'First St', 'Second Ave', 'Elm St', 'Maple Ave'])}"
                floor = random.choice([None, f"Floor {random.randint(1, 20)}"])
                apartment_no = random.choice([None, f"Apt {random.randint(1, 50)}"])
                address_type_id = random.choice(address_type_ids)
                is_default = 1 if i == 0 else 0  # First address is default

                self.cursor.execute(
                    """INSERT INTO customer_addresses
                       (customer_id, country, state, city, street, floor, appartment_no, address_type_id, is_default)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (customer_id, country, state, city, street, floor, apartment_no, address_type_id, is_default)
                )

        self.conn.commit()
        print("Seeded customer_addresses")

    def seed_product_categories(self):
        """Seed product categories with hierarchy"""
        # Parent categories
        parent_categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Books', 'Health & Beauty']

        category_hierarchy = {
            'Electronics': ['Smartphones', 'Laptops', 'Headphones', 'Cameras', 'Smart Watches'],
            'Clothing': ['Men\'s Wear', 'Women\'s Wear', 'Kids Wear', 'Shoes', 'Accessories'],
            'Home & Garden': ['Furniture', 'Kitchen', 'Decor', 'Garden Tools', 'Lighting'],
            'Sports': ['Fitness Equipment', 'Outdoor Gear', 'Team Sports', 'Water Sports'],
            'Books': ['Fiction', 'Non-fiction', 'Educational', 'Comics', 'Children\'s Books'],
            'Health & Beauty': ['Skincare', 'Makeup', 'Hair Care', 'Supplements', 'Personal Care']
        }

        # Insert parent categories first
        parent_ids = {}
        for category in parent_categories:
            self.cursor.execute("INSERT INTO product_categories (name) VALUES (%s)", (category,))
            parent_ids[category] = self.cursor.lastrowid

        # Insert subcategories
        for parent, subcategories in category_hierarchy.items():
            parent_id = parent_ids[parent]
            for subcategory in subcategories:
                self.cursor.execute(
                    "INSERT INTO product_categories (name, parent_category_id) VALUES (%s, %s)",
                    (subcategory, parent_id)
                )

        self.conn.commit()
        print("Seeded product_categories")

    def seed_brands(self):
        """Seed brands"""
        brands = [
            ('Apple', 'https://logo.apple.com'),
            ('Samsung', 'https://logo.samsung.com'),
            ('Nike', 'https://logo.nike.com'),
            ('Adidas', 'https://logo.adidas.com'),
            ('Sony', 'https://logo.sony.com'),
            ('Microsoft', 'https://logo.microsoft.com'),
            ('Google', 'https://logo.google.com'),
            ('Amazon', 'https://logo.amazon.com'),
            ('IKEA', 'https://logo.ikea.com'),
            ('H&M', 'https://logo.hm.com'),
            ('Zara', 'https://logo.zara.com'),
            ('Dell', 'https://logo.dell.com'),
            ('HP', 'https://logo.hp.com'),
            ('Canon', 'https://logo.canon.com'),
            ('Nikon', 'https://logo.nikon.com')
        ]

        for name, logo_url in brands:
            self.cursor.execute(
                "INSERT INTO brands (name, logo_url) VALUES (%s, %s)",
                (name, logo_url)
            )

        self.conn.commit()
        print("Seeded brands")

    def seed_products(self, count=200):
        """Seed products"""
        self.cursor.execute("SELECT brand_id FROM brands")
        brand_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT category_id FROM product_categories")
        category_ids = [row[0] for row in self.cursor.fetchall()]

        product_names = [
            'iPhone 15 Pro', 'MacBook Air M2', 'Samsung Galaxy S24', 'Dell XPS 13', 'Sony WH-1000XM5',
            'Nike Air Max 270', 'Adidas Ultraboost 22', 'IKEA Billy Bookshelf', 'H&M Cotton T-Shirt',
            'Canon EOS R6', 'Nikon D850', 'Apple Watch Series 9', 'Samsung Galaxy Watch 6',
            'Microsoft Surface Pro 9', 'Google Pixel 8', 'Sony PlayStation 5', 'Xbox Series X',
            'Nintendo Switch OLED', 'iPad Pro 12.9', 'AirPods Pro 2nd Gen', 'Samsung Galaxy Buds Pro',
            'Zara Wool Coat', 'Nike Running Shoes', 'Adidas Soccer Ball', 'IKEA Office Chair',
            'HP Pavilion Laptop', 'Canon Printer', 'Sony Bluetooth Speaker', 'Apple Magic Keyboard'
        ]

        descriptions = [
            'Premium quality product with advanced features',
            'Innovative design meets functionality',
            'Durable and reliable everyday essential',
            'Professional grade equipment for experts',
            'Comfortable and stylish for daily use',
            'High-performance technology at its best',
            'Eco-friendly and sustainable choice',
            'Perfect blend of style and comfort'
        ]

        for i in range(count):
            name = f"{random.choice(product_names)} - Model {random.randint(1000, 9999)}"
            description = random.choice(descriptions)
            brand_id = random.choice(brand_ids)
            category_id = random.choice(category_ids)
            created_at = self.generate_date_range(2022, 2024)

            self.cursor.execute(
                "INSERT INTO products (name, description, brand_id, category_id, created_at) VALUES (%s, %s, %s, %s, %s)",
                (name, description, brand_id, category_id, created_at)
            )

        self.conn.commit()
        print(f"Seeded {count} products")

    def seed_tags(self):
        """Seed product tags"""
        tags = [
            'bestseller', 'new', 'limited-edition', 'premium', 'eco-friendly', 'wireless', 'waterproof',
            'portable', 'professional', 'gaming', 'fitness', 'outdoor', 'indoor', 'vintage', 'modern',
            'compact', 'lightweight', 'heavy-duty', 'budget-friendly', 'luxury', 'smart', 'bluetooth',
            'usb-c', 'rechargeable', 'durable', 'comfortable', 'stylish', 'trendy', 'classic'
        ]

        for tag in tags:
            self.cursor.execute("INSERT INTO tags (name) VALUES (%s)", (tag,))

        self.conn.commit()
        print("Seeded tags")

    def seed_product_tags(self):
        """Assign random tags to products"""
        self.cursor.execute("SELECT product_id FROM products")
        product_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT tag_id FROM tags")
        tag_ids = [row[0] for row in self.cursor.fetchall()]

        for product_id in product_ids:
            # Each product gets 1-4 random tags
            num_tags = random.randint(1, 4)
            selected_tags = random.sample(tag_ids, num_tags)

            for tag_id in selected_tags:
                self.cursor.execute(
                    "INSERT INTO product_tags (product_id, tag_id) VALUES (%s, %s)",
                    (product_id, tag_id)
                )

        self.conn.commit()
        print("Seeded product_tags")

    def seed_product_to_categories(self):
        """Assign products to categories"""
        self.cursor.execute("SELECT product_id FROM products")
        product_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT category_id FROM product_categories")
        category_ids = [row[0] for row in self.cursor.fetchall()]

        for product_id in product_ids:
            # Each product belongs to 1-2 categories
            num_categories = random.randint(1, 2)
            selected_categories = random.sample(category_ids, num_categories)

            for category_id in selected_categories:
                self.cursor.execute(
                    "INSERT INTO product_to_categories (product_id, category_id) VALUES (%s, %s)",
                    (product_id, category_id)
                )

        self.conn.commit()
        print("Seeded product_to_categories")

    def seed_variant_options(self):
        """Seed variant options"""
        options = [
            ('Color', ['Red', 'Blue', 'Green', 'Black', 'White', 'Gray', 'Pink', 'Purple', 'Orange', 'Yellow']),
            ('Size', ['XS', 'S', 'M', 'L', 'XL', 'XXL']),
            ('Storage', ['64GB', '128GB', '256GB', '512GB', '1TB']),
            ('Material', ['Cotton', 'Polyester', 'Leather', 'Metal', 'Plastic', 'Glass'])
        ]

        for option_name, values in options:
            self.cursor.execute("INSERT INTO variant_options (name) VALUES (%s)", (option_name,))
            option_id = self.cursor.lastrowid

            for value in values:
                self.cursor.execute(
                    "INSERT INTO variant_option_values (option_id, value) VALUES (%s, %s)",
                    (option_id, value)
                )

        self.conn.commit()
        print("Seeded variant_options and values")

    def seed_product_variants(self):
        """Seed product variants"""
        self.cursor.execute("SELECT product_id FROM products")
        product_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT value_id, option_id FROM variant_option_values")
        variant_values = self.cursor.fetchall()

        # Get existing SKUs to avoid duplicates
        self.cursor.execute("SELECT sku FROM product_variants")
        existing_skus = set(row[0] for row in self.cursor.fetchall())

        for product_id in product_ids:
            # Each product gets 1-5 variants
            num_variants = random.randint(1, 5)

            for i in range(num_variants):
                # Generate unique SKU
                attempts = 0
                while attempts < 10:
                    sku = f"SKU-{product_id}-{random.randint(1000, 9999)}"
                    if sku not in existing_skus:
                        break
                    attempts += 1
                else:
                    continue  # Skip if can't generate unique SKU

                existing_skus.add(sku)
                unit_price = round(random.uniform(9.99, 999.99), 2)
                quantity_in_stock = random.randint(0, 500)
                created_at = self.generate_date_range(2022, 2024)

                self.cursor.execute(
                    """INSERT INTO product_variants (product_id, sku, unit_price, quantity_in_stock, created_at)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (product_id, sku, unit_price, quantity_in_stock, created_at)
                )
                variant_id = self.cursor.lastrowid

                # Assign 1-3 random variant options to each variant
                num_options = random.randint(1, 3)
                selected_values = random.sample(variant_values, num_options)

                for value_id, option_id in selected_values:
                    try:
                        self.cursor.execute(
                            "INSERT INTO variant_option_assignments (variant_id, value_id) VALUES (%s, %s)",
                            (variant_id, value_id)
                        )
                    except mysql.connector.IntegrityError:
                        pass  # Skip duplicates

        self.conn.commit()
        print("Seeded product_variants and variant_option_assignments")

    def seed_inventory_levels(self):
        """Seed inventory levels"""
        self.cursor.execute("SELECT variant_id, quantity_in_stock FROM product_variants")
        variants = self.cursor.fetchall()

        for variant_id, stock_qty in variants:
            self.cursor.execute(
                """INSERT INTO inventory_levels (variant_id, quantity_in_stock, created_at)
                   VALUES (%s, %s, %s)""",
                (variant_id, stock_qty, self.generate_date_range(2022, 2024))
            )

        self.conn.commit()
        print("Seeded inventory_levels")

    def seed_order_statuses(self):
        """Seed order statuses"""
        statuses = ['Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled', 'Returned']

        for status in statuses:
            try:
                self.cursor.execute("INSERT INTO order_statuses (name) VALUES (%s)", (status,))
            except mysql.connector.IntegrityError:
                pass  # Skip duplicates

        self.conn.commit()
        print("Seeded order_statuses")

    def seed_payment_methods(self):
        """Seed payment methods"""
        methods = [
            ('Credit Card', 'Visa'),
            ('Credit Card', 'Mastercard'),
            ('Credit Card', 'American Express'),
            ('PayPal', 'PayPal'),
            ('Bank Transfer', 'Wire Transfer'),
            ('Cash', 'Cash on Delivery')
        ]

        for method_type, name in methods:
            try:
                self.cursor.execute(
                    "INSERT INTO payment_methods (type, name) VALUES (%s, %s)",
                    (method_type, name)
                )
            except mysql.connector.IntegrityError:
                pass  # Skip duplicates

        self.conn.commit()
        print("Seeded payment_methods")

    def seed_payment_statuses(self):
        """Seed payment statuses"""
        statuses = ['Pending', 'Completed', 'Failed', 'Refunded', 'Cancelled']

        for status in statuses:
            try:
                self.cursor.execute("INSERT INTO payment_statuses (name) VALUES (%s)", (status,))
            except mysql.connector.IntegrityError:
                pass  # Skip duplicates

        self.conn.commit()
        print("Seeded payment_statuses")

    def seed_orders_and_related(self, count=800):
        """Seed orders, order items, invoices, payments, and shipments"""
        self.cursor.execute("SELECT customer_id FROM customers")
        customer_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT status_id FROM order_statuses")
        order_status_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT method_id FROM payment_methods")
        payment_method_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT status_id FROM payment_statuses")
        payment_status_ids = [row[0] for row in self.cursor.fetchall()]

        self.cursor.execute("SELECT variant_id, unit_price FROM product_variants WHERE quantity_in_stock > 0")
        available_variants = self.cursor.fetchall()

        for _ in range(count):
            customer_id = random.choice(customer_ids)

            # Get customer's addresses
            self.cursor.execute(
                "SELECT address_id FROM customer_addresses WHERE customer_id = %s",
                (customer_id,)
            )
            customer_addresses = [row[0] for row in self.cursor.fetchall()]
            address_id = random.choice(customer_addresses)

            status_id = random.choice(order_status_ids)
            created_at = self.generate_date_range(2022, 2024)

            # Create order
            self.cursor.execute(
                """INSERT INTO orders (created_at, status_id, customer_id, address_id)
                   VALUES (%s, %s, %s, %s)""",
                (created_at, status_id, customer_id, address_id)
            )
            order_id = self.cursor.lastrowid

            # Add order items (1-5 items per order)
            num_items = random.randint(1, 5)
            order_total = Decimal('0.00')

            selected_variants = random.sample(available_variants, min(num_items, len(available_variants)))

            for variant_id, variant_price in selected_variants:
                quantity = random.randint(1, 3)
                unit_price = variant_price

                self.cursor.execute(
                    """INSERT INTO order_items (order_id, variant_id, quantity, unit_price)
                       VALUES (%s, %s, %s, %s)""",
                    (order_id, variant_id, quantity, unit_price)
                )

                order_total += Decimal(str(unit_price)) * quantity

            # Create invoice
            tax = order_total * Decimal('0.08')  # 8% tax
            discount = Decimal(str(random.uniform(0, 50))) if random.random() < 0.3 else Decimal('0.00')
            invoice_total = order_total + tax - discount
            payment_total = invoice_total if random.random() < 0.9 else Decimal('0.00')  # 90% paid

            due_date = created_at + timedelta(days=30)
            payment_date = created_at + timedelta(days=random.randint(1, 15)) if payment_total > 0 else None

            self.cursor.execute(
                """INSERT INTO invoices (order_id, customer_id, invoice_total, tax, discount,
                   payment_total, invoice_date, due_date, payment_date)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (order_id, customer_id, invoice_total, tax, discount, payment_total,
                 created_at, due_date, payment_date)
            )
            invoice_id = self.cursor.lastrowid

            # Create payment if invoice is paid
            if payment_total > 0:
                method_id = random.choice(payment_method_ids)
                status_id = random.choice(payment_status_ids)

                self.cursor.execute(
                    """INSERT INTO payments (invoice_id, amount, payment_date, method_id, status_id)
                       VALUES (%s, %s, %s, %s, %s)""",
                    (invoice_id, payment_total, payment_date, method_id, status_id)
                )

            # Create shipment if order is shipped/delivered
            if status_id in [3, 4]:  # Shipped or Delivered status
                carriers = ['FedEx', 'UPS', 'DHL', 'USPS', 'Amazon Logistics']
                carrier = random.choice(carriers)
                tracking_number = f"TRK{random.randint(1000000000, 9999999999)}"
                shipment_date = created_at + timedelta(days=random.randint(1, 3))
                delivery_date = shipment_date + timedelta(days=random.randint(1, 7))

                self.cursor.execute(
                    """INSERT INTO shipments (carrier, tracking_number, shipment_date,
                       delivery_date, order_id, address_id)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (carrier, tracking_number, shipment_date, delivery_date, order_id, address_id)
                )

        self.conn.commit()
        print(f"Seeded {count} orders with related data")

    def run_all_seeds(self):
        """Run all seeding operations"""
        print("Starting database seeding...")

        # Clean database if requested
        if self.clean_start:
            self.clean_database()

        # Basic reference data
        self.seed_address_types()
        self.seed_order_statuses()
        self.seed_payment_methods()
        self.seed_payment_statuses()

        # Customer data
        self.seed_customers(500)
        self.seed_customer_addresses()

        # Product catalog
        self.seed_product_categories()
        self.seed_brands()
        self.seed_products(200)
        self.seed_tags()
        self.seed_product_tags()
        self.seed_product_to_categories()
        self.seed_variant_options()
        self.seed_product_variants()
        self.seed_inventory_levels()

        # Transactional data
        self.seed_orders_and_related(800)

        print("Database seeding completed successfully!")

    def close_connection(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()

# Usage example
if __name__ == "__main__":
    # Database configuration
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '0000',
        'database': 'my_store'
    }

    seeder = None
    try:
        # Set clean_start=True to clear all existing data first
        seeder = DatabaseSeeder(clean_start=True, **DB_CONFIG)
        seeder.run_all_seeds()
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if seeder:
            seeder.close_connection()