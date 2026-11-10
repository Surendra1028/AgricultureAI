from pydantic import BaseModel, Field
class CropInput(BaseModel):
    N: float = Field(ge=0, le=300)
    P: float = Field(ge=0, le=300)
    K: float = Field(ge=0, le=300)
    temperature: float = Field(ge=-10, le=60)
    humidity: float = Field(ge=0, le=100)
    ph: float = Field(ge=0, le=14)
    rainfall: float = Field(ge=0, le=1000)
class YieldInput(BaseModel):
    crop: str
    area_hectares: float = Field(gt=0)
    rainfall_mm: float = Field(ge=0, le=5000)
    average_temperature_c: float = Field(ge=-10, le=60)
    fertilizer_kg_per_hectare: float = Field(ge=0, le=5000)
    year: int = Field(ge=1950, le=2100)


class FertilizerInput(BaseModel):
    crop: str = Field(min_length=1, max_length=100)
    nitrogen: float = Field(ge=0, le=1000)
    phosphorus: float = Field(ge=0, le=1000)
    potassium: float = Field(ge=0, le=1000)


class FarmerCropInput(BaseModel):
    location: str = Field(min_length=2, max_length=120)
    land_acres: float = Field(gt=0, le=100000)
    season: str = Field(pattern=r"^(Kharif|Rabi|Summer)$")
    irrigation: str = Field(pattern=r"^(Rain-fed|Borewell|Canal|Other)$")
    soil_type: str = Field(default="Don't know", pattern=r"^(Red soil|Black soil|Sandy soil|Loamy soil|Don't know)$")
    previous_crop: str | None = Field(default=None, max_length=60)


class RegisterInput(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=190)
    password: str = Field(min_length=8, max_length=128)


class LoginInput(BaseModel):
    email: str = Field(min_length=5, max_length=190)
    password: str = Field(min_length=1, max_length=128)
