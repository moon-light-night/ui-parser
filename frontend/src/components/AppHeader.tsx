import { Link } from 'react-router-dom';
import { Sun, Moon, Monitor } from 'lucide-react';
import { THEME, useTheme } from '@/hooks/useTheme';
import { Button } from '@/components/ui/button';

interface AppHeaderProps {
  right?: React.ReactNode;
}

export function AppHeader({ right }: AppHeaderProps) {
  const { theme, toggle } = useTheme();

  return (
    <header className="bg-card border-b border-border px-6 h-14 flex items-center justify-between shrink-0 z-10">
      <Link
        to="/"
        className="flex items-center gap-2.5 hover:opacity-80 transition-opacity"
      >
        <div className="w-7 h-7 bg-primary rounded-lg flex items-center justify-center shrink-0">
          <Monitor className="w-4 h-4 text-primary-foreground" />
        </div>
        <span className="text-sm font-semibold text-foreground">UI Screenshots</span>
      </Link>

      <div className="flex items-center gap-2">
        {right}
        <Button
          variant="ghost"
          size="sm"
          onClick={toggle}
          title={theme === THEME.DARK ? 'Светлая тема' : 'Тёмная тема'}
        >
          {theme === THEME.DARK ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </Button>
      </div>
    </header>
  );
}
