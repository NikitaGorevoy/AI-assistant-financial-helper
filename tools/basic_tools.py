from newsapi import NewsApiClient
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from smolagents import Tool
import requests


class NewsTool(Tool):
    """
    Инструмент для поиска новостей на русском языке за указанный период.
    Всегда использует метод get_everything для получения наиболее релевантных результатов.
    """
    name = "news_fetcher"
    description = "Ищет новости на русском языке по ключевым словам за период с начала июня 2025 года. Возвращает топ-5 самых релевантных статей."
    inputs = {
        "query": {
            "type": "string",
            "description": "Ключевое слово или фраза для поиска (например: 'инфляция', 'курс доллара')",
            "required": True
        },
        "sort_by": {
            "type": "string",
            "description": "Критерий сортировки: relevancy (по релевантности), popularity (по популярности), publishedAt (по дате)",
            "default": "relevancy",
            "nullable": True
        }
    }
    output_type = "string"

    def __init__(self, api_key: str):
        super().__init__()
        if not api_key:
            raise ValueError("Необходим API ключ для NewsAPI")
        self.client = NewsApiClient(api_key=api_key)

    def forward(self, query: str, sort_by: Optional[str] = None) -> str:
        try:
            # Получаем новости за период с 1 июня 2025 года
            results = self.client.get_everything(
                q=query,
                from_param='2025-06-01',
                to=datetime.now().strftime('%Y-%m-%d'),
                language='ru',
                sort_by=sort_by or 'relevancy',
                page_size=5,
                page=1
            )

            articles = results.get('articles', [])
            
            if not articles:
                return f"Не найдено новостей по запросу: '{query}'"

            # Форматируем результат
            response = [
                "📰 Топ-5 самых релевантных новостей:",
                f"🔍 По запросу: '{query}'",
                f"📅 Период: 1 июня - {datetime.now().strftime('%d.%m.%Y')}",
                ""
            ]

            for idx, article in enumerate(articles[:5], 1):
                title = article.get('title', 'Без заголовка')
                source = article.get('source', {}).get('name', 'Неизвестный источник')
                date = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ').strftime('%d.%m.%Y')
                url = article.get('url', '')
                description = article.get('description', 'Нет описания')[:150] + '...' if article.get('description') else ''

                response.extend([
                    f"{idx}. {title}",
                    f"   📌 {description}",
                    f"   📆 {date} | 📰 {source}",
                    f"   🔗 Читать: {url}" if url else "",
                    ""
                ])

            return "\n".join(response)

        except Exception as e:
            return f"⚠️ Ошибка при поиске новостей: {str(e)}"


class CurrencyConversionTool(Tool):
    """Инструмент для конвертации валют с использованием API exchangerate-api.com."""
    name = "currency_converter"
    description = "Используется для конвертации валюты и получения актуальных курсов валют. Конвертирует указанную сумму из базовой валюты в целевую."
    inputs = {
        "base_currency": {"type": "string", "description": "Код валюты для конвертации (например, 'USD')."},
        "target_currency": {"type": "string", "description": "Код валюты, в которую нужно конвертировать (например, 'EUR')."},
        "amount": {"type": "number", "description": "Сумма базовой валюты для конвертации. По умолчанию 1.0.", "nullable": True}
    }
    output_type = "object"

    def __init__(self, api_key: str):
        """Инициализирует инструмент с ключом API.

        Args:
            api_key: Ключ API для exchangerate-api.com.
        """
        super().__init__()
        if not api_key:
            raise ValueError("Необходимо предоставить ключ API для CurrencyConversionTool")
        self.api_key = api_key

    def forward(self, base_currency: str, target_currency: str, amount: float = 1.0) -> Tuple[float, float]: 
        """Выполняет конвертацию валюты.

        Args:
            base_currency: Код валюты для конвертации. Например, 'USD'.
            target_currency: Код валюты, в которую нужно конвертировать. Например, 'EUR'.
            amount: Сумма для конвертации. По умолчанию 1.0.

        Returns:
            Tuple[float, float]: Кортеж, содержащий (conversion_rate, conversion_result), где
            conversion_rate - обменный курс между валютами, а
            conversion_result - сконвертированная сумма в целевой валюте.
        """
        endpoint = f"https://v6.exchangerate-api.com/v6/{self.api_key}/pair/{base_currency}/{target_currency}/{amount}"
        response = requests.get(endpoint)
        result = response.json()
        conversion_rate = result["conversion_rate"]
        conversion_result = result["conversion_result"]
        return conversion_rate, conversion_result
    

class TimeTool(Tool):
    """Инструмент для получения текущего времени и даты для местоположения."""
    name = "time_tool"
    description = "Получает текущее время и дату для указанного местоположения, используя идентификаторы часовых поясов IANA."    
    inputs = {
        "time_zone": {
            "type": "string", 
            "description": "Идентификатор часового пояса IANA (например, 'Europe/Moscow', 'America/New_York', 'Asia/Tokyo').", 
            "nullable": True
        }
    }
    output_type = "object"

    COMMON_TIMEZONES = [
        "Europe/Moscow", "Europe/London", "Europe/Paris", "Europe/Berlin", 
        "America/New_York", "America/Los_Angeles", "America/Chicago",
        "Asia/Tokyo", "Asia/Shanghai", "Asia/Dubai", "Asia/Kolkata",
        "Australia/Sydney", "Pacific/Auckland"
    ]

    def forward(self, time_zone: str = "Europe/Moscow") -> Dict[str, Any]:
        """Получает текущее время и дату для указанного часового пояса.

        Args:
            time_zone: Идентификатор часового пояса IANA (например, 'Europe/Moscow', 'America/New_York').
                       Полный список см. на https://en.wikipedia.org/wiki/List_of_tz_database_time_zones.

        Returns:
            Dict[str, Any]: Информация о текущем времени и дате для указанного часового пояса.
        """
        if "/" in time_zone:
            parts = time_zone.split("/", 1)
            area, location = parts[0], parts[1]
        else:
            area, location = time_zone, 
        
        if location:
            base_url = f"https://timeapi.io/api/Time/current/zone?timeZone={area}/{location}"
        else:
            base_url = f"https://timeapi.io/api/Time/current/zone?timeZone={area}"
            
        try:
            response = requests.get(base_url)
            response.raise_for_status()  
            
            result = response.json()
            
            if "dateTime" in result:
                result["summary"] = f"Текущее время в {time_zone}: {result['dateTime']}"
            
            return result
            
        except requests.exceptions.RequestException as e:
            error_message = f"Ошибка при получении данных времени: {str(e)}. "
            suggestions = ", ".join(self.COMMON_TIMEZONES[:5])
            error_message += f"Попробуйте один из этих распространенных часовых поясов: {suggestions}"
            raise ValueError(error_message)
