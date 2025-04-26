"""
Protocol fuzzing module for IoT devices.
"""

import asyncio
import random
import string
import struct
from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any, Optional
from loguru import logger

class FuzzingProtocol(Enum):
    HTTP = "http"
    MQTT = "mqtt"
    COAP = "coap"
    MODBUS = "modbus"
    CUSTOM = "custom"

@dataclass
class FuzzingResult:
    protocol: FuzzingProtocol
    input_data: bytes
    response: Optional[bytes]
    error: Optional[str]
    details: Dict[str, Any]

class ProtocolFuzzer:
    """Class for fuzzing IoT device protocols."""

    def __init__(self):
        self.max_payload_size = 4096
        self.iterations = 100
        self.timeout = 5.0

    async def fuzz(self, target: str, port: int, protocol: FuzzingProtocol) -> List[FuzzingResult]:
        """
        Perform protocol fuzzing on a target device.
        
        Args:
            target: Target device IP/hostname
            port: Target port
            protocol: Protocol to fuzz
            
        Returns:
            List of fuzzing results
        """
        logger.info(f"Starting protocol fuzzing for {target}:{port} using {protocol.value}")
        results = []

        try:
            if protocol == FuzzingProtocol.HTTP:
                results.extend(await self._fuzz_http(target, port))
            elif protocol == FuzzingProtocol.MQTT:
                results.extend(await self._fuzz_mqtt(target, port))
            elif protocol == FuzzingProtocol.COAP:
                results.extend(await self._fuzz_coap(target, port))
            elif protocol == FuzzingProtocol.MODBUS:
                results.extend(await self._fuzz_modbus(target, port))
            elif protocol == FuzzingProtocol.CUSTOM:
                results.extend(await self._fuzz_custom(target, port))
        except Exception as e:
            logger.error(f"Fuzzing failed: {e}")
            results.append(FuzzingResult(
                protocol=protocol,
                input_data=b"",
                response=None,
                error=str(e),
                details={"error_type": type(e).__name__}
            ))

        logger.info(f"Completed fuzzing with {len(results)} results")
        return results

    async def _fuzz_http(self, target: str, port: int) -> List[FuzzingResult]:
        """Fuzz HTTP protocol."""
        results = []
        methods = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
        paths = ["/", "/admin", "/api", "/debug", "/test", "/config"]
        headers = {
            "User-Agent": self._generate_random_string(),
            "Content-Type": "application/json",
            "X-Forwarded-For": self._generate_random_ip(),
            "Authorization": f"Bearer {self._generate_random_string()}"
        }

        reader, writer = await asyncio.open_connection(target, port)

        for _ in range(self.iterations):
            try:
                method = random.choice(methods)
                path = random.choice(paths)
                payload = self._generate_random_json()
                
                request = f"{method} {path} HTTP/1.1\r\n"
                request += f"Host: {target}:{port}\r\n"
                for key, value in headers.items():
                    request += f"{key}: {value}\r\n"
                request += f"Content-Length: {len(payload)}\r\n"
                request += "\r\n"
                request += payload

                writer.write(request.encode())
                await writer.drain()

                response = await asyncio.wait_for(reader.read(4096), timeout=self.timeout)
                
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.HTTP,
                    input_data=request.encode(),
                    response=response,
                    error=None,
                    details={
                        "method": method,
                        "path": path,
                        "headers": headers
                    }
                ))
            except Exception as e:
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.HTTP,
                    input_data=request.encode() if 'request' in locals() else b"",
                    response=None,
                    error=str(e),
                    details={"error_type": type(e).__name__}
                ))

        writer.close()
        await writer.wait_closed()
        return results

    async def _fuzz_mqtt(self, target: str, port: int) -> List[FuzzingResult]:
        """Fuzz MQTT protocol."""
        results = []
        packet_types = [
            0x10,  # CONNECT
            0x30,  # PUBLISH
            0x82,  # SUBSCRIBE
            0xE0   # DISCONNECT
        ]

        reader, writer = await asyncio.open_connection(target, port)

        for _ in range(self.iterations):
            try:
                packet_type = random.choice(packet_types)
                payload = self._generate_random_bytes()
                length = len(payload)
                
                # MQTT fixed header
                header = bytes([packet_type, length])
                
                writer.write(header + payload)
                await writer.drain()

                response = await asyncio.wait_for(reader.read(4096), timeout=self.timeout)
                
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.MQTT,
                    input_data=header + payload,
                    response=response,
                    error=None,
                    details={
                        "packet_type": hex(packet_type),
                        "length": length
                    }
                ))
            except Exception as e:
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.MQTT,
                    input_data=b"",
                    response=None,
                    error=str(e),
                    details={"error_type": type(e).__name__}
                ))

        writer.close()
        await writer.wait_closed()
        return results

    async def _fuzz_coap(self, target: str, port: int) -> List[FuzzingResult]:
        """Fuzz CoAP protocol."""
        results = []
        methods = [0x01, 0x02, 0x03, 0x04]  # GET, POST, PUT, DELETE
        
        transport, _ = await asyncio.get_event_loop().create_datagram_endpoint(
            lambda: asyncio.DatagramProtocol(),
            remote_addr=(target, port)
        )

        for _ in range(self.iterations):
            try:
                version = 0x40  # CoAP version 1
                method = random.choice(methods)
                token_length = random.randint(0, 8)
                message_id = random.randint(0, 65535)
                
                header = bytes([
                    version | method,
                    0,  # No options
                    (message_id >> 8) & 0xFF,
                    message_id & 0xFF
                ])
                
                token = self._generate_random_bytes(token_length)
                payload = self._generate_random_bytes()
                
                transport.sendto(header + token + payload)
                
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.COAP,
                    input_data=header + token + payload,
                    response=None,  # UDP is connectionless
                    error=None,
                    details={
                        "method": hex(method),
                        "message_id": message_id,
                        "token_length": token_length
                    }
                ))
            except Exception as e:
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.COAP,
                    input_data=b"",
                    response=None,
                    error=str(e),
                    details={"error_type": type(e).__name__}
                ))

        transport.close()
        return results

    async def _fuzz_modbus(self, target: str, port: int) -> List[FuzzingResult]:
        """Fuzz Modbus protocol."""
        results = []
        function_codes = [
            0x01,  # Read Coils
            0x02,  # Read Discrete Inputs
            0x03,  # Read Holding Registers
            0x04,  # Read Input Registers
            0x05,  # Write Single Coil
            0x06   # Write Single Register
        ]

        reader, writer = await asyncio.open_connection(target, port)

        for _ in range(self.iterations):
            try:
                transaction_id = random.randint(0, 65535)
                protocol_id = 0  # Modbus protocol
                function_code = random.choice(function_codes)
                unit_id = random.randint(0, 255)
                
                # Modbus header
                header = struct.pack(">HHHB",
                    transaction_id,
                    protocol_id,
                    2,  # Length of remaining message
                    unit_id
                )
                
                # Function code and payload
                payload = bytes([function_code]) + self._generate_random_bytes()
                
                writer.write(header + payload)
                await writer.drain()

                response = await asyncio.wait_for(reader.read(4096), timeout=self.timeout)
                
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.MODBUS,
                    input_data=header + payload,
                    response=response,
                    error=None,
                    details={
                        "transaction_id": transaction_id,
                        "function_code": hex(function_code),
                        "unit_id": unit_id
                    }
                ))
            except Exception as e:
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.MODBUS,
                    input_data=b"",
                    response=None,
                    error=str(e),
                    details={"error_type": type(e).__name__}
                ))

        writer.close()
        await writer.wait_closed()
        return results

    async def _fuzz_custom(self, target: str, port: int) -> List[FuzzingResult]:
        """Fuzz with custom protocol mutations."""
        results = []
        reader, writer = await asyncio.open_connection(target, port)

        for _ in range(self.iterations):
            try:
                # Generate random payload with various mutations
                payload = self._generate_mutated_payload()
                
                writer.write(payload)
                await writer.drain()

                response = await asyncio.wait_for(reader.read(4096), timeout=self.timeout)
                
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.CUSTOM,
                    input_data=payload,
                    response=response,
                    error=None,
                    details={"payload_size": len(payload)}
                ))
            except Exception as e:
                results.append(FuzzingResult(
                    protocol=FuzzingProtocol.CUSTOM,
                    input_data=b"",
                    response=None,
                    error=str(e),
                    details={"error_type": type(e).__name__}
                ))

        writer.close()
        await writer.wait_closed()
        return results

    def _generate_random_string(self, length: int = 16) -> str:
        """Generate a random string."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    def _generate_random_bytes(self, length: int = None) -> bytes:
        """Generate random bytes."""
        if length is None:
            length = random.randint(1, self.max_payload_size)
        return bytes(random.randint(0, 255) for _ in range(length))

    def _generate_random_ip(self) -> str:
        """Generate a random IP address."""
        return '.'.join(str(random.randint(0, 255)) for _ in range(4))

    def _generate_random_json(self) -> str:
        """Generate random JSON data."""
        data = {
            "id": random.randint(1, 1000),
            "name": self._generate_random_string(),
            "value": random.random(),
            "data": [self._generate_random_string() for _ in range(3)]
        }
        return str(data)

    def _generate_mutated_payload(self) -> bytes:
        """Generate a mutated payload with various fuzzing techniques."""
        mutation_types = [
            self._bit_flip_mutation,
            self._byte_flip_mutation,
            self._repeat_mutation,
            self._truncate_mutation,
            self._append_mutation
        ]
        
        base_payload = self._generate_random_bytes()
        mutator = random.choice(mutation_types)
        return mutator(base_payload)

    def _bit_flip_mutation(self, data: bytes) -> bytes:
        """Flip random bits in the payload."""
        result = bytearray(data)
        num_flips = random.randint(1, len(data))
        for _ in range(num_flips):
            pos = random.randint(0, len(data) - 1)
            bit = random.randint(0, 7)
            result[pos] ^= (1 << bit)
        return bytes(result)

    def _byte_flip_mutation(self, data: bytes) -> bytes:
        """Flip random bytes in the payload."""
        result = bytearray(data)
        num_flips = random.randint(1, len(data))
        for _ in range(num_flips):
            pos = random.randint(0, len(data) - 1)
            result[pos] = random.randint(0, 255)
        return bytes(result)

    def _repeat_mutation(self, data: bytes) -> bytes:
        """Repeat sections of the payload."""
        if not data:
            return data
        start = random.randint(0, len(data) - 1)
        length = random.randint(1, len(data) - start)
        repeat = random.randint(2, 4)
        section = data[start:start + length]
        return data[:start] + section * repeat + data[start + length:]

    def _truncate_mutation(self, data: bytes) -> bytes:
        """Truncate the payload at a random position."""
        if not data:
            return data
        pos = random.randint(0, len(data))
        return data[:pos]

    def _append_mutation(self, data: bytes) -> bytes:
        """Append random data to the payload."""
        append_length = random.randint(1, 100)
        return data + self._generate_random_bytes(append_length) 