-- Sample products for development / seeding
INSERT INTO products (title, retailer_name, price, category, brand, colors, style_tags, image_url, product_url, affiliate_url)
VALUES
  ('Floral Wrap Dress',      'Zara',           59.99, 'dress',        'Zara',           ARRAY['pink','white'],   ARRAY['romantic','bohemian'],   'https://picsum.photos/400/600?random=10', 'https://zara.com/p1',    'https://zara.com/p1?ref=shopper'),
  ('Classic White Blazer',   'H&M',            89.99, 'jacket',       'H&M',            ARRAY['white'],          ARRAY['minimalist','formal'],   'https://picsum.photos/400/600?random=11', 'https://hm.com/p2',      'https://hm.com/p2?ref=shopper'),
  ('High-Rise Straight Jeans','Levi''s',        79.00, 'jeans',        'Levi''s',        ARRAY['blue','navy'],    ARRAY['casual','streetwear'],   'https://picsum.photos/400/600?random=12', 'https://levis.com/p3',   'https://levis.com/p3?ref=shopper'),
  ('Silk Cami Top',          '& Other Stories', 45.00, 'top',          '& Other Stories',ARRAY['beige','neutral'],ARRAY['minimalist','romantic'],  'https://picsum.photos/400/600?random=13', 'https://stories.com/p4', 'https://stories.com/p4?ref=shopper'),
  ('Oversized Trench Coat',  'Mango',          149.00, 'coat',         'Mango',          ARRAY['beige','brown'],  ARRAY['minimalist','formal'],   'https://picsum.photos/400/600?random=14', 'https://mango.com/p5',   'https://mango.com/p5?ref=shopper'),
  ('Leather Mini Skirt',     'ASOS',            69.00, 'skirt',        'ASOS',           ARRAY['black'],          ARRAY['edgy','streetwear'],     'https://picsum.photos/400/600?random=15', 'https://asos.com/p6',    'https://asos.com/p6?ref=shopper'),
  ('Strappy Sandals',        'Steve Madden',    55.00, 'shoes',        'Steve Madden',   ARRAY['beige','nude'],   ARRAY['casual','romantic'],     'https://picsum.photos/400/600?random=16', 'https://stevemadden.com/p7','https://stevemadden.com/p7?ref=shopper'),
  ('Chunky Knit Sweater',    'Weekday',         65.00, 'top',          'Weekday',        ARRAY['beige','grey'],   ARRAY['casual','minimalist'],   'https://picsum.photos/400/600?random=17', 'https://weekday.com/p8', 'https://weekday.com/p8?ref=shopper'),
  ('Printed Midi Skirt',     'Topshop',         49.00, 'skirt',        'Topshop',        ARRAY['pink','floral'],  ARRAY['bohemian','romantic'],   'https://picsum.photos/400/600?random=18', 'https://topshop.com/p9', 'https://topshop.com/p9?ref=shopper'),
  ('Structured Tote Bag',    'Charles & Keith', 119.00,'bag',          'Charles & Keith',ARRAY['black','brown'],  ARRAY['minimalist','formal'],   'https://picsum.photos/400/600?random=19', 'https://charleskeith.com/p10','https://charleskeith.com/p10?ref=shopper')
ON CONFLICT DO NOTHING;
