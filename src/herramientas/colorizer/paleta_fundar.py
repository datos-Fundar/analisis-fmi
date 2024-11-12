from .color import Color

blanco  = Color.from_hex('#F5F5F5').as_rgb()
negro   = Color.from_hex("#151515").as_rgb()

# Primarios

celeste         = Color.from_hex('#7BB5C4').as_rgb()
verde_claro     = Color.from_hex('#9FC1AD').as_rgb()
offwhite        = Color.from_hex('#D3D3E0').as_rgb()
violeta         = Color.from_hex('#8d9bff').as_rgb()
naranja         = Color.from_hex('#FF9750').as_rgb()
amarillo        = Color.from_hex('#FFD900').as_rgb()

primarios = [
    celeste,
    verde_claro,
    offwhite,
    violeta,
    naranja,
    amarillo,
]

# Secundarios

celeste_claro       = Color.from_hex('#B5E0EA').as_rgb()
gris_claro          = Color.from_hex('#B3B3B3').as_rgb()
gris_oscuro         = Color.from_hex('#848279').as_rgb()
beis_oscuro         = Color.from_hex('#AFA36E').as_rgb()
verde_oscuro        = Color.from_hex('#5D896F').as_rgb()
violeta_desaturado  = Color.from_hex('#9C9CBC').as_rgb()
naranja_saturado    = Color.from_hex('#E27124').as_rgb()

secundarios = [
    celeste_claro,
    gris_claro,
    gris_oscuro,
    beis_oscuro,
    verde_oscuro,
    violeta_desaturado,
    naranja_saturado,
]