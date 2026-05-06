from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app import models  # noqa: F401
from backend.app.db.base import Base
from backend.app.services.amap_service_poi_fetcher import AMapServicePoiFetcher


def test_service_poi_upsert_allows_missing_cost_rating():
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    db = sessionmaker(bind=engine, future=True)()
    fetcher = AMapServicePoiFetcher(db)
    result = fetcher.upsert_service_pois([{
        "amap_poi_id": "amap-test-1",
        "name": "测试餐饮",
        "city": "重庆",
        "nearby_area": "解放碑片区",
        "service_type": "restaurant",
        "price_level": "unknown",
        "source": "amap",
    }])
    assert result["inserted"] == 1
    assert len(fetcher.fetch_service_pois_by_area("重庆", "解放碑片区", "restaurant")) == 1
