# Copyright (c) 2022-2026, The Isaac Lab Project Developers (https://github.com/isaac-sim/IsaacLab/blob/main/CONTRIBUTORS.md).
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Tests for DisplayPort cable-insertion environment configuration."""

import pytest

from isaaclab_tasks.contrib.deploy.cable_insertion.config.displayport_rizon_4s.joint_pos_env_cfg import (
    Rizon4sGravDisplayportInsertionEnvCfg,
    Rizon4sGravDisplayportInsertionNoJointVelEnvCfg,
)
from isaaclab_tasks.contrib.deploy.cable_insertion.config.displayport_rizon_4s.task_space_env_cfg import (
    Rizon4sTaskSpaceDisplayportInsertionEnvCfg,
)
from isaaclab_tasks.contrib.deploy.cable_insertion.displayport_insertion_env_cfg import DP_ROBOT_USD_ENV_VAR

_CALIBRATED_USD_NAME = "Rizon4s-063459_with_Grav_calibrated_kinematics.usd"

_JOINT_SPACE_CFGS = (
    Rizon4sGravDisplayportInsertionEnvCfg,
    Rizon4sGravDisplayportInsertionNoJointVelEnvCfg,
)
_ALL_CFGS = _JOINT_SPACE_CFGS + (Rizon4sTaskSpaceDisplayportInsertionEnvCfg,)


@pytest.fixture(autouse=True)
def _clear_override(monkeypatch):
    """Keep the ambient environment from deciding which robot the assertions see."""
    monkeypatch.delenv(DP_ROBOT_USD_ENV_VAR, raising=False)


@pytest.mark.parametrize("env_cfg_cls", _JOINT_SPACE_CFGS)
def test_joint_space_spawns_the_calibrated_robot_by_default(env_cfg_cls):
    """Joint-space policies command joints directly, so they default to the calibrated arm."""
    assert env_cfg_cls().scene.robot.spawn.usd_path.endswith(_CALIBRATED_USD_NAME)


def test_task_space_keeps_the_stock_robot_by_default():
    """Task space never set a ``usd_path`` of its own, and the override must not change that."""
    usd_path = Rizon4sTaskSpaceDisplayportInsertionEnvCfg().scene.robot.spawn.usd_path
    assert not usd_path.endswith(_CALIBRATED_USD_NAME)


@pytest.mark.parametrize("env_cfg_cls", _ALL_CFGS)
@pytest.mark.parametrize(
    "override",
    (
        "/tmp/calibrated_rizon4s.usd",
        "omniverse://localhost/Library/calibrated_rizon4s.usd",
        "https://example.invalid/assets/calibrated_rizon4s.usd",
    ),
    ids=("local", "omniverse", "http"),
)
def test_dp_robot_usd_selects_the_robot_in_both_control_spaces(monkeypatch, env_cfg_cls, override):
    """A calibrated description may live on disk, on Nucleus, or behind a URL."""
    monkeypatch.setenv(DP_ROBOT_USD_ENV_VAR, override)
    assert env_cfg_cls().scene.robot.spawn.usd_path == override


@pytest.mark.parametrize("env_cfg_cls", _ALL_CFGS)
@pytest.mark.parametrize("blank", ("", "   "), ids=("empty", "whitespace"))
def test_blank_dp_robot_usd_falls_back_to_the_default(monkeypatch, env_cfg_cls, blank):
    """An exported-but-empty variable must not blank out the robot."""
    monkeypatch.delenv(DP_ROBOT_USD_ENV_VAR, raising=False)
    expected = env_cfg_cls().scene.robot.spawn.usd_path
    monkeypatch.setenv(DP_ROBOT_USD_ENV_VAR, blank)
    assert env_cfg_cls().scene.robot.spawn.usd_path == expected
