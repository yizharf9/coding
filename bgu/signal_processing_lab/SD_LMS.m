function [Wout, WConv, Er] = SD_LMS(Win, InSig, RefSig, U);
%     Steepest-descent LMS adaptive algorithm
%     ---------------------------------------
% Input :
%--------
% Win - Starting weights (column vector)
% InSig - input signal  (for multi inputs inSig is an array)
% RefSig - refference signals (Desired response)
% U - convergence rate
%
% Output :
%---------
% Wout - Output weights
% WConv - convergence of weights
% Er - error signal
%

Wsize = size(Win);, if Wsize(1,2)~=1, error(' Win - should be a column vector'), end
Wsize = max(Wsize);

[C, Ln] = size(InSig);, if C~=1 & C~=Wsize, error(' InSig - should be a row vector'), end
MultiRef = 0;
if C==Wsize, MultiRef = 1;, end

[Rc, Rr] = size(RefSig);
if Rc~=1, error(' RefSig - wrong number of columns'), end
if Rr~=Ln, error(' RefSig - should be in the length of InSig'), end

Wout = Win;
WConv = zeros(Wsize, Ln);
Er = zeros(1, Ln);


for a=1:Ln
  if MultiRef,
    Sig = InSig(:,a);
  else
    if a<Wsize,
      Sig = zeros(Wsize, 1);
      Sig(1:a) = InSig(a:-1:1);
    else
      Sig = InSig(a:-1:(a-Wsize+1))';
    end
  end

  Out = Wout' * Sig;

  Er(a:a) = RefSig(a:a) - Out;

  Wout = Wout - U * (-2) * Sig * Er(a:a);
  WConv(:,a) = Wout ;

end, %next a

end

