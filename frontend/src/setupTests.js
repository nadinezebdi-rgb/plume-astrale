import { TextDecoder, TextEncoder } from 'util';
import '@testing-library/jest-dom';

globalThis.TextDecoder = TextDecoder;
globalThis.TextEncoder = TextEncoder;
