#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import time
from mcrcon import MCRcon


def get_settings():
    """
    Get info for connecting rcon from the env.

    Returns
    -------
    (host, passwd, port) : (str, str, int)
    """

    host = os.getenv("RCON_HOST")
    if host is None:
        host = "localhost"

    passwd = os.getenv("RCON_PASSWORD")
    if passwd is None:
        passwd = "testing"

    port = os.getenv("RCON_PORT")
    if port is None:
        port = "25575"

    return host, passwd, int(port)


class Torching(object):

    def __init__(self, mcr, mod=6, dn=2, dy_max=1):
        """
        Parmeters
        ---------
        mcr : connected MCRcon

        mod : int, optional (default=6)
            何マスおきに松明を設置するか

        dn : int, optional (default=2)
            一度にplayerの周囲何本分先まで松明を設置するか

        dy_max : int, optional (default=1)
            段差があるときに上下どこまで追加で判定するか

        Note
        ----
        1人のplayerだけがloginしている状況を想定
        """
        self.mcr = mcr
        self.mod = mod
        self.dn = dn
        self.dy_max = dy_max

        # '{player} has the following entity data: "minecraft:{data}"'
        # から{data}を抜き出す正規表現
        self.entity = re.compile(r'(?<=minecraft:).*(?=")')

        # '{player} has the following entity data: [{x}d, {y}d, {z}d]'
        # から{x}d, {y}d, {z}dを抜き出す正規表現
        self.position = re.compile(r"(?<=\[).*(?=\])")

    def _run(self, cmd, debug=False):
        """
        Run the minecraft command.

        Parameters
        ----------
        cmd : str

        debug : bool, optional (default=False)
            If True, print the cmd and the response.
        """
        res = self.mcr.command(cmd)
        if debug:
            print(f"cmd: {cmd}")
            print(f"response: {res}")
        return res

    def what_in_the_left(self):
        """
        Return what the player have in the left hand.

        Returns
        -------
        block_name : str
        """

        res = self._run("data get entity @p Inventory[{Slot:-106b}].id")
        if res == "No entity was found":
            raise SystemExit(res)
        if res.startswith("Found no elements"):
            # empty
            return ""
        block_name = self.entity.search(res).group(0)
        return block_name

    def get_world_name(self):
        """
        Return the current world name in which the player is.

        Returns
        -------
        wn : str
        """

        res = self._run("data get entity @p Dimension")
        if res == "No entity was found":
            raise SystemExit(res)
        wn = self.entity.search(res).group(0)
        return wn

    def get_current_position(self):
        """
        Return the current player position.

        Returns
        -------
        (xp, yp, zp) : (float, float, float)
        """

        res = self._run("data get entity @p Pos")
        if res == 'No entity was found':
            raise SystemExit(res)
        pos = self.position.search(res).group(0)

        # "{x}d, {y}d, {z}d"からdを取り除いて,で分割
        pos_array = pos.replace("d", "").split(",")

        # float <- str
        xp, yp, zp = [float(s.strip()) for s in pos_array]
        return xp, yp, zp

    def on_the_ground(self, wn, x, y, z):
        """
        Check whether (x, y, z) is on the ground.

        Parameters
        ----------
        wn : int
            world name

        x : int

        y : int

        z : int

        Returns
        -------
        out : bool
        """
        # 1個下が草ブロックなら
        res = self._run(f"execute in minecraft:{wn} if block {x} {y-1} {z} minecraft:grass_block")
        if res == 'Test passed':
            return True
        else:
            return False

    def _set_torch(self, wn, x, y, z):
        """
        Set torch if (x, y, z) is air and (x, y-1, z) is grass block.

        Parameters
        ----------
        wn : str

        x : int

        y : int

        z : int

        Returns
        -------
        out : int
            0 - success
            1 - (x, y, z) is not air, you should try on upper.
           -1 - (x, y, z) is air but not on the ground, you should try on lower.
        """

        res = self._run(f"execute in minecraft:{wn} if block {x} {y} {z} minecraft:torch")
        if res == 'Test passed':
            # already exists
            return 0

        # 草が生えていたら十分条件
        res = self._run(f"execute in minecraft:{wn} if block {x} {y} {z} minecraft:grass run setblock {x} {y} {z} minecraft:torch")
        if res.startswith("Changed the block"):
            return 0

        res = self._run(f"execute in minecraft:{wn} if block {x} {y} {z} minecraft:air")
        if res == 'Test passed':

            # 空気ブロックかつ一個下が草ブロックなら
            res = self._run(f"execute in minecraft:{wn} if block {x} {y-1} {z} minecraft:grass_block run setblock {x} {y} {z} minecraft:torch")
            if res.startswith("Changed the block"):
                return 0

            else:
                # 空気ブロックだが松明を置けなかった場合
                return -1

        else:
            # 空気ブロックじゃない場合
            return 1

    def search_ground_and_set(self, wn, x, y, z):
        """
        (x, y, z)に松明を設置
        設置できなかった場合は{self.dy_max}の範囲で上下方向に地面を探索して設置

        Parameters
        ----------
        x : int

        y : int

        z : int
        """

        res = self._set_torch(wn, x, y, z)
        if res == 0:
            # success
            return

        # try to find the ground and set torch
        #   bit = 1  : upward
        #   bit = -1 : downward
        bit = res
        for dy in range(self.dy_max):
            res = self._set_torch(wn, x, y+(bit)*(dy+1), z)
            if res == 0:
                return

    def _exec(self, xp, yp, zp):
        """
        playerが草ブロックの上にいるとき、{self.mod}の倍数の位置にだけ松明を設置
        (ただし、建築の妨害をしないためにpalyerに一番近い場所には設置しない)

        Parameters
        -----------
        xp : float
            player position 0

        yp : float
            player position 1

        zp : float
            player position 2
        """

        # get the current world name
        wn = self.get_world_name()

        # int <- float
        x, y, z = [int(p) for p in [xp, yp, zp]]
        if not self.on_the_ground(wn, x, y, z):
            # the player is not on the ground, skip
            return

        # get the nearest index
        xi = round(xp/self.mod)
        zj = round(zp/self.mod)

        # walk around the player
        for i in range(-self.dn, self.dn+1):
            for j in range(-self.dn, self.dn+1):
                if i == 0 and j == 0:
                    # skip the nearest one
                    continue

                # back to int
                x = (xi + i)*self.mod
                z = (zj + j)*self.mod

                self.search_ground_and_set(wn, x, y, z)

    def main(self, dt=1.0):
        """
        playerが左手に松明を持っているときにだけ実行

        Parameters
        ----------
        dt : float, optional (default=1.0)
            interval in [sec]
            (小さくしすぎると高負荷)
        """

        # initialize
        xp, yp, zp = 0, 0, 0

        # infinite loop
        while True:

            # take interval
            time.sleep(dt)

            # skip if torch is not in the left
            block_name = self.what_in_the_left()
            if not block_name == "torch":
                continue

            # store the previous value
            xp_old, yp_old, zp_old = xp, yp, zp

            # reload
            xp, yp, zp = self.get_current_position()
            if xp == xp_old and yp == yp_old and zp == zp_old:
                # the player is not moving, skip
                continue

            # playerの周囲に松明を設置
            self._exec(xp, yp, zp)


if __name__ == "__main__":

    with MCRcon(*get_settings()) as mcr:

        torching = Torching(mcr)
        torching.main()
