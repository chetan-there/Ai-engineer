PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS products (
  product_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  category TEXT NOT NULL,
  aliases_json TEXT NOT NULL,
  tags_json TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS customers (
  customer_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS orders (
  order_id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  status TEXT NOT NULL,
  delivery_eta TEXT NOT NULL,
  purchase_date TEXT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS warranty_policies (
  product_id TEXT PRIMARY KEY,
  months INTEGER NOT NULL,
  requires_order INTEGER NOT NULL,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS warranty_registrations (
  registration_id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL,
  product_id TEXT NOT NULL,
  serial_number TEXT NOT NULL,
  order_id TEXT,
  registered_at TEXT NOT NULL,
  warranty_start_date TEXT NOT NULL,
  warranty_end_date TEXT NOT NULL,
  status TEXT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_warranty_serial ON warranty_registrations(product_id, serial_number);

CREATE TABLE IF NOT EXISTS support_cases (
  case_id TEXT PRIMARY KEY,
  customer_id TEXT NOT NULL,
  product_id TEXT,
  order_id TEXT,
  intent TEXT NOT NULL,
  status TEXT NOT NULL,
  summary TEXT NOT NULL,
  escalated INTEGER NOT NULL,
  outcome TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE IF NOT EXISTS knowledge_documents (
  doc_id TEXT PRIMARY KEY,
  product_id TEXT,
  kind TEXT NOT NULL,
  title TEXT NOT NULL,
  text TEXT NOT NULL,
  source_url TEXT,
  updated_at TEXT,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);
