from __future__ import annotations

from typing import Literal, Union
from collections.abc import Iterable
from pydantic import BaseModel
from itertools import product
import pytest
import instructor
from .util import models, modes


class Weather(BaseModel):
    location: str
    units: Literal["imperial", "metric"]


class GoogleSearch(BaseModel):
    query: str


def test_sync_parallel_tools__error(client):
    client = instructor.patch(client, mode=instructor.Mode.PARALLEL_TOOLS)

    with pytest.raises(TypeError):
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You must always use tools"},
                {
                    "role": "user",
                    "content": "What is the weather in toronto and dallas and who won the super bowl?",
                },
            ],
            response_model=Weather,
        )


def test_sync_parallel_tools_or(client):
    client = instructor.from_openai(client, mode=instructor.Mode.PARALLEL_TOOLS)
    resp = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You must always use tools"},
            {
                "role": "user",
                "content": "What is the weather in toronto and dallas and who won the super bowl?",
            },
        ],
        response_model=Iterable[Union[Weather, GoogleSearch]],
    )
    resp_list = list(resp)
    for resp_item in resp_list:
        assert isinstance(resp_item, tuple)
        assert isinstance(resp_item[0], str)
        assert isinstance(resp_item[1], BaseModel)
    assert len(resp_list) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("model, mode", product(models, modes))
async def test_async_parallel_tools_or(model, mode, aclient):
    client = instructor.from_openai(aclient, mode=mode)
    resp = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You must always use tools"},
            {
                "role": "user",
                "content": "What is the weather in toronto and dallas and who won the super bowl?",
            },
        ],
        response_model=Iterable[Union[Weather, GoogleSearch]],
    )
    resp_list = list(resp)
    for resp_item in resp_list:
        assert isinstance(resp_item, BaseModel)
    assert len(resp_list) == 3


def test_sync_parallel_tools_one(client):
    client = instructor.patch(client, mode=instructor.Mode.PARALLEL_TOOLS)
    resp = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You must always use tools"},
            {
                "role": "user",
                "content": "What is the weather in toronto and dallas?",
            },
        ],
        response_model=Iterable[Weather],
    )
    # assert len(list(resp)) == 2
    resp_list = list(resp)
    for resp_item in resp_list:
        assert isinstance(resp_item, tuple)
        assert isinstance(resp_item[0], str)
        assert isinstance(resp_item[1], Weather)
    assert len(resp_list) == 2


@pytest.mark.asyncio
async def test_async_parallel_tools_one(aclient):
    client = instructor.patch(aclient, mode=instructor.Mode.PARALLEL_TOOLS)
    resp = await client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": "You must always use tools"},
            {
                "role": "user",
                "content": "What is the weather in toronto and dallas?",
            },
        ],
        response_model=Iterable[Weather],
    )
    resp_list = list(resp)
    for resp_item in resp_list:
        assert isinstance(resp_item, tuple)
        assert isinstance(resp_item[0], str)
        assert isinstance(resp_item[1], Weather)
