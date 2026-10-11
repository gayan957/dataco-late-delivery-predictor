export const SCHEDULED_DAYS = {
  'Same Day':       0,
  'First Class':    1,
  'Second Class':   2,
  'Standard Class': 4,
}

export const SHIPPING_MODES = ['Standard Class', 'Second Class', 'First Class', 'Same Day']
export const SEGMENTS        = ['Consumer', 'Corporate', 'Home Office']
export const MARKETS         = ['Africa', 'Europe', 'LATAM', 'Pacific Asia', 'USCA']

export const SHIPPING_INFO = {
  'Same Day':       { days: 0, icon: '⚡', desc: 'Same-day delivery',      color: '#06b6d4' },
  'First Class':    { days: 1, icon: '🚀', desc: 'Next-day delivery',        color: '#6366f1' },
  'Second Class':   { days: 2, icon: '📬', desc: '2-day standard delivery',  color: '#8b5cf6' },
  'Standard Class': { days: 4, icon: '📦', desc: '4-day economy delivery',   color: '#64748b' },
}

export const LATE_TIPS = {
  'Same Day':       'Same Day is still predicted late. Expedite warehouse processing immediately.',
  'First Class':    'Consider upgrading to Same Day delivery if the order is critical.',
  'Second Class':   'Upgrade to First Class (1d) or Same Day to prevent late delivery.',
  'Standard Class': 'Consider upgrading to Second Class (2d) or First Class (1d).',
}

export const CATEGORIES = [
  "Accessories", "As Seen on  TV!", "Baby ", "Baseball & Softball",
  "Basketball", "Books ", "Boxing & MMA", "CDs ", "Cameras ",
  "Camping & Hiking", "Cardio Equipment", "Children's Clothing", "Cleats",
  "Computers", "Consumer Electronics", "Crafts", "DVDs", "Electronics",
  "Fishing", "Fitness Accessories", "Garden", "Girls' Apparel",
  "Golf Apparel", "Golf Bags & Carts", "Golf Balls", "Golf Gloves",
  "Golf Shoes", "Health and Beauty", "Hockey", "Hunting & Shooting",
  "Indoor/Outdoor Games", "Kids' Golf Clubs", "Lacrosse", "Men's Clothing",
  "Men's Footwear", "Men's Golf Clubs", "Music", "Pet Supplies",
  "Shop By Sport", "Soccer", "Sporting Goods", "Strength Training",
  "Tennis & Racquet", "Toys", "Trade-In", "Video Games", "Water Sports",
  "Women's Apparel", "Women's Clothing", "Women's Golf Clubs",
].sort()

const PRIORITY_COUNTRIES = [
  'Estados Unidos','México','Francia','Alemania','Brasil','España',
  'China','India','Australia','Canada','Reino Unido','Italia','Japón',
]

const ALL_COUNTRIES = [
  'Afganistán','Albania','Alemania','Angola','Arabia Saudí','Argelia',
  'Argentina','Armenia','Australia','Austria','Azerbaiyán','Bangladés',
  'Barbados','Baréin','Belice','Benín','Bielorrusia','Bolivia',
  'Bosnia y Herzegovina','Botsuana','Brasil','Bulgaria','Burkina Faso',
  'Burundi','Bután','Bélgica','Camboya','Camerún','Canada','Chile',
  'China','Chipre','Colombia','Corea del Sur','Costa Rica',
  'Costa de Marfil','Croacia','Cuba','Dinamarca','Ecuador','Egipto',
  'El Salvador','Emiratos Árabes Unidos','Eritrea','Eslovaquia',
  'Eslovenia','España','Estados Unidos','Estonia','Etiopía',
  'Filipinas','Finlandia','Francia','Gabón','Georgia','Ghana',
  'Grecia','Guadalupe','Guatemala','Guayana Francesa','Guinea',
  'Guinea Ecuatorial','Guinea-Bissau','Guyana','Haití','Honduras',
  'Hong Kong','Hungría','India','Indonesia','Irak','Irlanda','Irán',
  'Israel','Italia','Jamaica','Japón','Jordania','Kazajistán','Kenia',
  'Kirguistán','Kuwait','Laos','Lesoto','Liberia','Libia','Lituania',
  'Luxemburgo','Líbano','Macedonia','Madagascar','Malasia','Mali',
  'Marruecos','Martinica','Mauritania','Moldavia','Mongolia',
  'Montenegro','Mozambique','Myanmar (Birmania)','México','Namibia',
  'Nepal','Nicaragua','Nigeria','Noruega','Nueva Zelanda','Níger',
  'Omán','Pakistán','Panamá','Papúa Nueva Guinea','Paraguay',
  'Países Bajos','Perú','Polonia','Portugal','Qatar','Reino Unido',
  'República Centroafricana','República Checa',
  'República Democrática del Congo','República Dominicana',
  'República de Gambia','República del Congo','Ruanda','Rumania',
  'Rusia','Senegal','Serbia','Sierra Leona','Singapur','Siria',
  'Somalia','Sri Lanka','Suazilandia','SudAfrica','Sudán',
  'Sudán del Sur','Suecia','Suiza','Surinam','Tailandia','Taiwán',
  'Tanzania','Tayikistán','Togo','Trinidad y Tobago','Turkmenistán',
  'Turquía','Túnez','Ucrania','Uganda','Uruguay','Uzbekistán',
  'Venezuela','Vietnam','Yemen','Yibuti','Zambia','Zimbabue',
]

export const COUNTRIES = [
  ...PRIORITY_COUNTRIES,
  ...ALL_COUNTRIES.filter(c => !PRIORITY_COUNTRIES.includes(c)).sort(),
]
