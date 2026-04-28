import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import UploadDialog from '../UploadDialog';

const mockCreateUploadUrl = vi.fn();
const mockUploadToS3 = vi.fn();
const mockRegisterScreenshot = vi.fn();

vi.mock('@/api', () => ({
  screenshotApi: {
    createUploadUrl: (...args: unknown[]) => mockCreateUploadUrl(...args),
    registerScreenshot: (...args: unknown[]) => mockRegisterScreenshot(...args),
  },
  s3Api: {
    uploadToS3: (...args: unknown[]) => mockUploadToS3(...args),
  },
}));

function renderDialog(onClose = vi.fn(), onUploaded = vi.fn()) {
  return render(<UploadDialog onClose={onClose} onUploaded={onUploaded} />);
}

function makeFile(name: string, type: string) {
  return new File(['data'], name, { type });
}

describe('UploadDialog — валидация типа файла', () => {
  it('показывает ошибку для неподдерживаемого типа', async () => {
    renderDialog();
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, { target: { files: [makeFile('doc.pdf', 'application/pdf')] } });
    expect(await screen.findByText(/Неподдерживаемый тип файла/)).toBeInTheDocument();
  });

  it('принимает корректный тип image/png', async () => {
    renderDialog();
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    fireEvent.change(input, { target: { files: [makeFile('shot.png', 'image/png')] } });
    expect(await screen.findByText('shot.png')).toBeInTheDocument();
    expect(screen.queryByText(/Неподдерживаемый тип файла/)).not.toBeInTheDocument();
  });
});

describe('UploadDialog — успешный upload', () => {
  beforeEach(() => {
    mockCreateUploadUrl.mockResolvedValue({
      response: {
        uploadUrl: 'http://minio/upload',
        storageBucket: 'screenshots',
        storageKey: 'abc.png',
      },
    });
    mockUploadToS3.mockImplementation((_url: string, _file: File, onProgress: (p: number) => void) => {
      onProgress(100);
      return Promise.resolve();
    });
    mockRegisterScreenshot.mockResolvedValue({ response: { screenshot: { id: 's1' } } });
  });

  it('вызывает onUploaded после успешной загрузки', async () => {
    const onUploaded = vi.fn();
    renderDialog(vi.fn(), onUploaded);

    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    await userEvent.upload(input, makeFile('shot.png', 'image/png'));
    await userEvent.click(screen.getByRole('button', { name: /загрузить/i }));

    await waitFor(() => expect(onUploaded).toHaveBeenCalledOnce());
  });

  it('показывает ошибку если createUploadUrl падает', async () => {
    mockCreateUploadUrl.mockRejectedValue(new Error('S3 unavailable'));

    renderDialog();
    const input = document.querySelector('input[type="file"]') as HTMLInputElement;
    await userEvent.upload(input, makeFile('shot.png', 'image/png'));
    await userEvent.click(screen.getByRole('button', { name: /загрузить/i }));

    expect(await screen.findByText(/S3 unavailable/)).toBeInTheDocument();
  });
});
