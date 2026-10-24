
import os
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

import httpx
from openai import AsyncOpenAI
from uagents import Agent, Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    ChatAcknowledgement,
    TextContent,
    chat_protocol_spec
)

agent = Agent()
protocol = Protocol(spec=chat_protocol_spec)

client = AsyncOpenAI(
    base_url=os.environ["ASI1_BASE_URL"],
    api_key=os.environ["ASI1_API_KEY"]
)


def reply(text):
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)]
    )


async def fetch_data(city):
    async with httpx.AsyncClient(timeout=25) as http:

        try:
            geo = await http.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": city,
                    "count": 5,
                    "format": "json"
                }
            )
            geo.raise_for_status()

            results = geo.json().get("results", [])

            if not results:
                return None

            place = next(
                (p for p in results if p.get("country_code") == "IN"),
                results[0]
            )

            lat = place["latitude"]
            lon = place["longitude"]

        except Exception:
            return None

        async def weather():
            try:
                r = await http.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": lat,
                        "longitude": lon,
                        "current": (
                            "temperature_2m,"
                            "precipitation,"
                            "wind_speed_10m"
                        ),
                        "timezone": "auto"
                    }
                )

                r.raise_for_status()
                return str(r.json().get("current", {}))

            except Exception as e:
                return "Weather unavailable: " + str(e)

        async def resources():

            query = f"""
            [out:json][timeout:15];
            (
              node["amenity"="hospital"](around:5000,{lat},{lon});
              way["amenity"="hospital"](around:5000,{lat},{lon});
              node["amenity"="pharmacy"](around:5000,{lat},{lon});
              way["amenity"="pharmacy"](around:5000,{lat},{lon});
            );
            out center 20;
            """

            endpoints = [
                "https://overpass.kumi.systems/api/interpreter",
                "https://overpass-api.de/api/interpreter"
            ]

            for endpoint in endpoints:
                try:
                    r = await http.post(
                        endpoint,
                        data={"data": query}
                    )

                    r.raise_for_status()

                    items = []

                    for x in r.json().get("elements", []):
                        tags = x.get("tags", {})
                        pos = x.get("center", x)

                        items.append({
                            "name": tags.get("name", "Unnamed"),
                            "type": tags.get("amenity"),
                            "lat": pos.get("lat"),
                            "lon": pos.get("lon")
                        })

                    return str(items)

                except Exception:
                    continue

            return "Resource search unavailable from both endpoints."

        w, r = await asyncio.gather(
            weather(),
            resources()
        )

        return (
            f"Verified location: {place['name']}, "
            f"{place.get('country', '')}\n"
            f"Coordinates: {lat}, {lon}\n"
            f"Weather API result: {w}\n"
            f"OpenStreetMap resources: {r}\n"
            "Weather source: https://open-meteo.com/\n"
            "Map source: https://www.openstreetmap.org/"
        )


@protocol.on_message(ChatMessage)
async def handle(ctx: Context, sender: str, msg: ChatMessage):

    await ctx.send(
        sender,
        ChatAcknowledgement(
            timestamp=datetime.now(timezone.utc),
            acknowledged_msg_id=msg.msg_id
        )
    )

    user_text = msg.text()

    if not user_text:
        return

    try:
        # STEP 1: Extract location

        if "roorkee" in user_text.lower():
            city = "Roorkee"

        else:
            extraction = await client.chat.completions.create(
                model="asi1",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Extract only the city name from the "
                            "user's message. Return UNKNOWN if "
                            "no city is specified. Do not invent."
                        )
                    },
                    {
                        "role": "user",
                        "content": user_text
                    }
                ],
                max_tokens=50
            )

            city = (
                extraction.choices[0].message.content or ""
            ).strip().strip('"').strip("'")

            city = city.replace("City:", "").strip()

        if not city or city.upper() == "UNKNOWN":

            await ctx.send(
                sender,
                reply(
                    "Please provide your city. "
                    "Example: Roorkee, India."
                )
            )
            return

        # STEP 2: Execute external tools

        data = await fetch_data(city)

        if data is None:
            await ctx.send(
                sender,
                reply(
                    "I could not verify that location. "
                    "Please provide a valid city name."
                )
            )
            return

        # STEP 3: AI generates action plan

        result = await client.chat.completions.create(
            model="asi1",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ResQ AI Coordinator, an "
                        "emergency readiness planning agent. "
                        "Analyze the supplied external tool results. "
                        "Create a prioritized actionable plan "
                        "for college event organizers. "
                        "Include weather, nearby resources, "
                        "risk assessment and preparation checklist. "
                        "Never invent hospitals, phone numbers, "
                        "live availability or emergency dispatch. "
                        "Clearly mention failed or missing tool data. "
                        "Advise contacting local emergency services "
                        "directly in immediate emergencies."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Request: {user_text}\n\n"
                        f"External tool results:\n{data}"
                    )
                }
            ],
            max_tokens=1200
        )

        answer = result.choices[0].message.content

        await ctx.send(
            sender,
            reply(answer or "Unable to generate the plan.")
        )

    except Exception:
        ctx.logger.exception("ResQ processing failed")

        await ctx.send(
            sender,
            reply(
                "A processing error occurred. "
                "Please retry or check Agent Logs."
            )
        )


@protocol.on_message(ChatAcknowledgement)
async def handle_ack(
    ctx: Context,
    sender: str,
    msg: ChatAcknowledgement
):
    pass


agent.include(protocol, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
