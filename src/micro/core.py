from __future__ import annotations
from fastapi import FastAPI
from functools import wraps
from typing import Callable
import inspect
from deta import Deta
import os
from typing import Optional


class Micro(FastAPI):

    _exportable: Micro = None

    @property
    def deta(self) -> Optional[Deta]:
        try:
            return Deta(os.getenv("DETA_PROJECT_KEY"))
        except Exception:
            return None

    @staticmethod
    def startup_task(func: Callable) -> None:
        if not inspect.iscoroutinefunction(func):
            try:
                func()
            except:
                pass

    def cron(self, func: Callable) -> None:
        if len(inspect.getfullargspec(func).args) == 1:
            try:
                from detalib.app import App
            except ImportError:
                pass
            else:
                def wrapped_cron(event):
                    if not inspect.iscoroutinefunction(func):
                        return func(event.__dict__)

                app = App(self)
                app.lib._cron.populate_cron(wrapped_cron)
                self._exportable = app

    @property
    def export(self) -> Micro:
        return self._exportable or self
