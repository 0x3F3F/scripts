#!/usr/bin/perl

use strict;

# IRB:
# Copied from: https://gist.github.com/codemedic/4552022


sub on_start {
    my ($self) = @_;

    $self->{copy_cmd} = $self->x_resource('copyCommand') || 'xclip -l 1 -selection clipboard';
    $self->{paste_cmd} = $self->x_resource('pasteClipboardCommand') || 'xclip -l 1 -o -selection clipboard';
    $self->{paste_primary_cmd} = $self->x_resource('pastePrimaryCommand') || 'xclip -l 1 -o -selection primary';
    $self->{copy_primary_cmd} = $self->x_resource('copyPrimaryCommand') || 'xsel -ip';

    ()
}

sub copy {
    my ($self) = @_;

    if (open(CLIPBOARD, "| $self->{copy_cmd}")) {
        my $sel = $self->selection();
        utf8::encode($sel);
        print CLIPBOARD $sel;
        close(CLIPBOARD);
    } else {
        print STDERR "error running '$self->{copy_cmd}': $!\n";
    }

    ()
}

sub paste {
    my ($self) = @_;

    my $str = `$self->{paste_cmd}`;
    if ($? == 0) {
        $self->tt_paste($self->locale_encode($str));
    } else {
        print STDERR "error running '$self->{paste_cmd}': $!\n";
    }

    ()
}


sub paste_primary {
    my ($self) = @_;

    my $str = `$self->{paste_primary_cmd}`;
    if ($? == 0) {
        $self->tt_paste($self->locale_encode($str));
    } else {
        print STDERR "error running '$self->{paste_cmd}': $!\n";
    }

    ()
}

sub on_user_command {
    my ($self, $cmd) = @_;
    if ($cmd eq "clipboard:paste") {
        $self->paste;
    }
    elsif ($cmd eq "clipboard:paste_primary") {
        $self->paste_primary;
    }
    elsif ($cmd eq "clipboard:copy") {
        $self->copy;
    }
}

sub on_sel_grab {
    my ($self, $cmd) = @_;
	my $query = $self->selection;
	open (my $pipe,'|-',$self->{copy_primary_cmd}) or die;
	print $pipe $query;
	close $pipe;
}
