/*
 * Copyright (c) Pavol Rusnak, SatoshiLabs
 *
 * Licensed under Microsoft Reference Source License (Ms-RSL)
 * see LICENSE.md file for details
 */

#include <stdio.h>
#include <string.h>
#include <stdint.h>

#include "py/nlr.h"
#include "py/runtime.h"
#include "py/binary.h"
#include "py/mphal.h"

#if MICROPY_PY_TREZORMSG

#if defined STM32_HAL_H
#include "modtrezormsg-stmhal.h"
#elif defined UNIX
#include "modtrezormsg-unix.h"
#else
#error Unsupported port. Only STMHAL and UNIX ports are supported.
#endif

typedef struct _mp_obj_Msg_t {
    mp_obj_base_t base;
} mp_obj_Msg_t;

STATIC mp_obj_t mod_TrezorMsg_Msg_make_new(const mp_obj_type_t *type, size_t n_args, size_t n_kw, const mp_obj_t *args) {
    mp_arg_check_num(n_args, n_kw, 0, 0, false);
    msg_init();
    mp_obj_Msg_t *o = m_new_obj(mp_obj_Msg_t);
    o->base.type = type;
    return MP_OBJ_FROM_PTR(o);
}

/// def trezor.msg.send(iface: int, message: bytes) -> int
///
/// Sends message using USB HID (device) or UDP (emulator).
///
STATIC mp_obj_t mod_TrezorMsg_Msg_send(mp_obj_t self, mp_obj_t iface, mp_obj_t message) {
    uint8_t iface_num = mp_obj_get_int(iface);
    mp_buffer_info_t msg;
    mp_get_buffer_raise(message, &msg, MP_BUFFER_READ);
    ssize_t r = msg_send(iface_num, msg.buf, msg.len);
    return MP_OBJ_NEW_SMALL_INT(r);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(mod_TrezorMsg_Msg_send_obj, mod_TrezorMsg_Msg_send);

#define TICK_RESOLUTION 1000

/// def trezor.msg.select(timeout_us: int) -> tuple
///
/// Polls the event queue and returns the event object.
/// Function returns None if timeout specified in microseconds is reached.
///
STATIC mp_obj_t mod_TrezorMsg_Msg_select(mp_obj_t self, mp_obj_t timeout_us) {
    int timeout = mp_obj_get_int(timeout_us);
    if (timeout < 0) {
        timeout = 0;
    }
    for(;;) {
        uint32_t e = msg_poll_ui_event();
        if (e) {
            mp_obj_tuple_t *tuple = MP_OBJ_TO_PTR(mp_obj_new_tuple(3, NULL));
            tuple->items[0] = MP_OBJ_NEW_SMALL_INT((e & 0xFF0000) >> 16);
            tuple->items[1] = MP_OBJ_NEW_SMALL_INT((e & 0xFF00) >> 8);
            tuple->items[2] = MP_OBJ_NEW_SMALL_INT((e & 0xFF));
            return MP_OBJ_FROM_PTR(tuple);
        }
        uint8_t iface;
        uint8_t recvbuf[64];
        ssize_t l = msg_recv(&iface, recvbuf, 64);
        if (l > 0) {
            vstr_t vstr;
            vstr_init_len(&vstr, l);
            memcpy(vstr.buf, recvbuf, l);
            mp_obj_tuple_t *tuple = MP_OBJ_TO_PTR(mp_obj_new_tuple(3, NULL));
            tuple->items[0] = MP_OBJ_NEW_SMALL_INT(8);
            tuple->items[1] = MP_OBJ_NEW_SMALL_INT(iface);
            tuple->items[2] = mp_obj_new_str_from_vstr(&mp_type_bytes, &vstr);
            return MP_OBJ_FROM_PTR(tuple);
         }
        if (timeout <= 0) {
            break;
        }
#if defined UNIX
        mp_hal_delay_us(TICK_RESOLUTION);
#else
        mp_hal_delay_us_fast(TICK_RESOLUTION);
#endif
        timeout -= TICK_RESOLUTION;
    }
    return mp_const_none;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_2(mod_TrezorMsg_Msg_select_obj, mod_TrezorMsg_Msg_select);

STATIC const mp_rom_map_elem_t mod_TrezorMsg_Msg_locals_dict_table[] = {
    { MP_ROM_QSTR(MP_QSTR_select), MP_ROM_PTR(&mod_TrezorMsg_Msg_select_obj) },
    { MP_ROM_QSTR(MP_QSTR_send), MP_ROM_PTR(&mod_TrezorMsg_Msg_send_obj) },
};
STATIC MP_DEFINE_CONST_DICT(mod_TrezorMsg_Msg_locals_dict, mod_TrezorMsg_Msg_locals_dict_table);

STATIC const mp_obj_type_t mod_TrezorMsg_Msg_type = {
    { &mp_type_type },
    .name = MP_QSTR_Msg,
    .make_new = mod_TrezorMsg_Msg_make_new,
    .locals_dict = (void*)&mod_TrezorMsg_Msg_locals_dict,
};

STATIC const mp_rom_map_elem_t mp_module_TrezorMsg_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_TrezorMsg) },
    { MP_ROM_QSTR(MP_QSTR_Msg), MP_ROM_PTR(&mod_TrezorMsg_Msg_type) },
};

STATIC MP_DEFINE_CONST_DICT(mp_module_TrezorMsg_globals, mp_module_TrezorMsg_globals_table);

const mp_obj_module_t mp_module_TrezorMsg = {
    .base = { &mp_type_module },
    .name = MP_QSTR_TrezorMsg,
    .globals = (mp_obj_dict_t*)&mp_module_TrezorMsg_globals,
};

#endif // MICROPY_PY_TREZORMSG
