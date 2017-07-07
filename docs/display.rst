Display Module
**************

.. module:: rgb

Utilities
=========

.. function:: color565(r, g, b)

    Convert red, green and blue values (0-255) into a 16-bit 565 encoding.

.. class:: DummyPin()

    Can be used in place of a ``Pin()`` when you want to skip it.


Display Class
=============

This is the interface that all the display classes share.

.. class:: Display(width, height)

    .. method:: init()

        Run the initialization commands for the given display (ran
        automatically when the object is created).

    .. method:: pixel(x, y, color)

        Get or set the value of a pixel at the given position.

    .. method:: fill_rectangle(x, y, width, height, color)

        Draw a rectangle at specified position with specified width and
        height, and fill it with the specified color.

    .. method:: fill(color)

        Fill the whole display with the specified color.

    .. method:: hline(x, y, width, color)

        Draw a horizontal line.

    .. method:: vline(x, y, height, color)

        Draw a vertical line.

    ..method:: blit_buffer(buffer, x, y, width, height)

        Copy the pixels from the buffer onto the display, starting at position
        ``(x, y)`` and assuming the copied area has width ``width`` and height
        ``height``. The area has to fit entirely inside the display
