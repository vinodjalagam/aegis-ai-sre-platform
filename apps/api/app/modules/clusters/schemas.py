from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class ClusterBase(BaseModel):
    """
    Shared cluster fields.
    """

    name: str = Field(
        min_length=3,
        max_length=100,
    )

    description: str | None = None

    provider: str = Field(
        min_length=2,
        max_length=50,
    )


class ClusterCreate(ClusterBase):
    """
    Schema used to create a cluster.
    """

    kubeconfig: str = Field(
        min_length=1,
    )


class ClusterUpdate(BaseModel):
    """
    Schema used to update a cluster.
    """

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=100,
    )

    description: str | None = None

    provider: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
    )

    kubeconfig: str | None = None

    status: str | None = None

    is_active: bool | None = None


class ClusterResponse(ClusterBase):
    """
    Cluster returned by the API.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str
    is_active: bool


class ClusterListResponse(BaseModel):
    """
    List of clusters.
    """

    items: list[ClusterResponse]
    total: int