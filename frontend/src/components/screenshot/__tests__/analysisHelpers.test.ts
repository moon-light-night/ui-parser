import { describe, it, expect } from 'vitest';
import {
  screenshotImageUrl,
  severityVariant,
  severityLabel,
  priorityVariant,
  priorityLabel,
  formatBytes,
} from '../analysisHelpers';
import { Severity, Priority } from '@/proto/generated/common';

const S3_DEFAULT = 'http://localhost:9000';

describe('screenshotImageUrl', () => {
  it('возвращает storageUrl если он есть', () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const s = { storageUrl: 'https://cdn.example.com/img.png', storageBucket: '', storageKey: '' } as any;
    expect(screenshotImageUrl(s)).toBe('https://cdn.example.com/img.png');
  });

  it('строит URL из bucket+key если нет storageUrl', () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const s = { storageUrl: '', storageBucket: 'screenshots', storageKey: 'abc.png' } as any;
    expect(screenshotImageUrl(s)).toBe(`${S3_DEFAULT}/screenshots/abc.png`);
  });

  it('возвращает null если нет ни url ни bucket/key', () => {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const s = { storageUrl: '', storageBucket: '', storageKey: '' } as any;
    expect(screenshotImageUrl(s)).toBeNull();
  });
});

describe('severityVariant', () => {
  it.each([
    [Severity.LOW,    'success'],
    [Severity.MEDIUM, 'warning'],
    [Severity.HIGH,   'destructive'],
    [Severity.UNSPECIFIED, 'secondary'],
  ])('Severity.%s → %s', (s, expected) => {
    expect(severityVariant(s)).toBe(expected);
  });
});

describe('severityLabel', () => {
  it.each([
    [Severity.LOW,    'Low'],
    [Severity.MEDIUM, 'Medium'],
    [Severity.HIGH,   'High'],
    [Severity.UNSPECIFIED, '?'],
  ])('Severity.%s → %s', (s, expected) => {
    expect(severityLabel(s)).toBe(expected);
  });
});

describe('priorityVariant', () => {
  it.each([
    [Priority.LOW,    'secondary'],
    [Priority.MEDIUM, 'default'],
    [Priority.HIGH,   'warning'],
    [Priority.UNSPECIFIED, 'secondary'],
  ])('Priority.%s → %s', (p, expected) => {
    expect(priorityVariant(p)).toBe(expected);
  });
});

describe('priorityLabel', () => {
  it.each([
    [Priority.LOW,    'Low'],
    [Priority.MEDIUM, 'Medium'],
    [Priority.HIGH,   'High'],
    [Priority.UNSPECIFIED, '?'],
  ])('Priority.%s → %s', (p, expected) => {
    expect(priorityLabel(p)).toBe(expected);
  });
});

describe('formatBytes', () => {
  it('форматирует байты меньше 1 KB', () => {
    expect(formatBytes(512)).toBe('512 B');
  });

  it('форматирует килобайты', () => {
    expect(formatBytes(2048)).toBe('2 KB');
  });

  it('форматирует мегабайты', () => {
    expect(formatBytes(1.5 * 1024 * 1024)).toBe('1.5 MB');
  });

  it('принимает bigint', () => {
    expect(formatBytes(BigInt(1024))).toBe('1 KB');
  });
});
